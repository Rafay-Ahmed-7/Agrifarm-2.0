"""SQL Server repository compatible with the existing AgriFarm views.

Optimized with high-performance persistent connection management,
smart read-caching, parallel pre-warming, and immediate write-invalidation.
"""

from __future__ import annotations

import os
import threading
import concurrent.futures
from decimal import Decimal, InvalidOperation

import pyodbc


SERVER   = os.getenv("AGRIFARM_SQL_SERVER",   "IT-Tauheed")
DATABASE = os.getenv("AGRIFARM_SQL_DATABASE", "AgriFarm")
DRIVER   = os.getenv("AGRIFARM_SQL_DRIVER",   "ODBC Driver 18 for SQL Server")

_lock = threading.RLock()
_shared_conn: pyodbc.Connection | None = None
_cache: dict = {}

# Thread-pool used for background pre-warming (max 1 worker keeps it lightweight)
_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="agrifarm-db")


def _create_raw_connection() -> pyodbc.Connection:
    return pyodbc.connect(
        f"DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};"
        "Trusted_Connection=yes;TrustServerCertificate=yes;",
        autocommit=False,
    )


def _connection() -> pyodbc.Connection:
    """Returns a healthy, reusable connection with automatic reconnection on drop."""
    global _shared_conn
    with _lock:
        if _shared_conn is not None:
            try:
                _shared_conn.execute("SELECT 1")
                return _shared_conn
            except Exception:
                try:
                    _shared_conn.close()
                except Exception:
                    pass
                _shared_conn = None

        _shared_conn = _create_raw_connection()
        return _shared_conn


def invalidate_cache(key: str | None = None):
    """Clears cached read queries when a mutation occurs."""
    global _cache
    with _lock:
        if key:
            _cache.pop(key, None)
        else:
            _cache.clear()


def pre_warm() -> "concurrent.futures.Future":
    """Fire-and-forget: establish the SQL connection and prime ALL read caches
    in the background thread-pool so the first UI render hits cache (< 1 ms).
    Returns the Future so callers can optionally wait on it.
    """
    def _run():
        try:
            _connection()
            get_fields()
            get_crops_with_fields()
            get_inventory()
            get_dashboard_metrics()
            get_upcoming_activities(30)
            get_activity_logs()
        except Exception:
            pass
    return _executor.submit(_run)


def _result(success: bool, value):
    return success, value


def test_connection():
    try:
        conn = _connection()
        conn.execute("SELECT 1").fetchone()
        return _result(True, "SQL Server connection successful")
    except Exception as exc:
        return _result(False, str(exc))


def initialize_db():
    """Verify the already-applied schema and ensure ActivityLogs exists."""
    required = {"Fields", "Crops", "InventoryItems", "InventoryTransactions"}
    try:
        conn = _connection()
        # Ensure ActivityLogs table exists
        conn.execute(
            "IF OBJECT_ID(N'dbo.ActivityLogs', N'U') IS NULL "
            "CREATE TABLE dbo.ActivityLogs ("
            "  [LogId] bigint IDENTITY(1,1) NOT NULL PRIMARY KEY,"
            "  [ActionType] nvarchar(50) NOT NULL,"
            "  [EntityType] nvarchar(50) NOT NULL,"
            "  [EntityName] nvarchar(200) NOT NULL,"
            "  [Details] nvarchar(500) NULL,"
            "  [PerformedAt] datetime2(0) NOT NULL CONSTRAINT DF_ActivityLogs_PerformedAt DEFAULT SYSUTCDATETIME()"
            ");"
        )
        conn.commit()

        rows = conn.execute(
            "SELECT name FROM sys.tables WHERE schema_id = SCHEMA_ID('dbo')"
        ).fetchall()
        actual = {row[0] for row in rows}
        missing = required - actual
        if missing:
            return _result(False, f"Missing SQL Server tables: {sorted(missing)}")
        return _result(True, "SQL Server schema verified")
    except Exception as exc:
        return _result(False, str(exc))


def record_log(conn, action_type: str, entity_type: str, entity_name: str, details: str | None = None):
    """Internal helper to insert an activity log within an existing transaction or connection."""
    try:
        conn.execute(
            "INSERT INTO dbo.ActivityLogs (ActionType, EntityType, EntityName, Details) VALUES (?, ?, ?, ?)",
            action_type, entity_type, entity_name, details
        )
    except Exception:
        pass


def get_activity_logs(limit: int = 150):
    """Fetches chronological activity logs with formatted timestamps."""
    cache_key = f"activity_logs_{limit}"
    with _lock:
        if cache_key in _cache:
            return list(_cache[cache_key])
        try:
            conn = _connection()
            rows = conn.execute(
                "SELECT LogId AS id, ActionType AS action_type, EntityType AS entity_type, "
                "EntityName AS entity_name, Details AS details, "
                "CONVERT(varchar(19), PerformedAt, 120) AS performed_at "
                "FROM dbo.ActivityLogs ORDER BY LogId DESC"
            ).fetchmany(limit)
            keys = ("id", "action_type", "entity_type", "entity_name", "details", "performed_at")
            result = [dict(zip(keys, row)) for row in rows]
            _cache[cache_key] = result
            return list(result)
        except Exception:
            return []


def clear_activity_logs():
    """Clears all activity logs."""
    try:
        with _lock:
            conn = _connection()
            conn.execute("TRUNCATE TABLE dbo.ActivityLogs")
            conn.commit()
            invalidate_cache()
            record_log(conn, "System Init", "System", "Activity Logs", "Log history cleared by operator")
            conn.commit()
        return _result(True, "Activity logs cleared")
    except Exception as exc:
        return _result(False, str(exc))


def get_fields():
    with _lock:
        if "fields" in _cache:
            return list(_cache["fields"])
        conn = _connection()
        rows = conn.execute(
            "SELECT FieldId AS id, Name AS name, AreaAcres AS area_acres, "
            "SoilType AS soil_type, Status AS status "
            "FROM dbo.Fields WHERE IsArchived = 0 ORDER BY Name"
        ).fetchall()
        result = [dict(zip(("id", "name", "area_acres", "soil_type", "status"), row)) for row in rows]
        _cache["fields"] = result
        return list(result)


def get_crops_with_fields():
    with _lock:
        if "crops" in _cache:
            return list(_cache["crops"])
        conn = _connection()
        rows = conn.execute(
            "SELECT c.CropId AS id, c.Name AS name, c.Variety AS variety, "
            "f.Name AS field_name, c.PlantingDate AS planting_date, "
            "c.ExpectedHarvestDate AS expected_harvest, c.GrowthStage AS stage "
            "FROM dbo.Crops c JOIN dbo.Fields f ON f.FieldId = c.FieldId "
            "WHERE c.IsArchived = 0 ORDER BY c.ExpectedHarvestDate, c.Name"
        ).fetchall()
        keys = ("id", "name", "variety", "field_name", "planting_date", "expected_harvest", "stage")
        result = [dict(zip(keys, row)) for row in rows]
        _cache["crops"] = result
        return list(result)


def add_field(name, area_acres, soil_type, status):
    try:
        with _lock:
            conn = _connection()
            conn.execute(
                "INSERT dbo.Fields (Name, AreaAcres, SoilType, Status) VALUES (?, ?, ?, ?)",
                name, area_acres, soil_type or None, status,
            )
            record_log(conn, "Register Field", "Field", name, f"Registered {area_acres} acres ({status}, {soil_type or 'Default'})")
            conn.commit()
            invalidate_cache()
        return _result(True, "Field added")
    except Exception as exc:
        return _result(False, str(exc))


def update_field(field_id, name, area_acres, soil_type, status):
    try:
        with _lock:
            conn = _connection()
            conn.execute(
                "UPDATE dbo.Fields SET Name=?, AreaAcres=?, SoilType=?, Status=?, UpdatedAt=SYSUTCDATETIME() "
                "WHERE FieldId=? AND IsArchived=0",
                name, area_acres, soil_type or None, status, field_id,
            )
            record_log(conn, "Update Field", "Field", name, f"Updated to {area_acres} acres, status: {status}")
            conn.commit()
            invalidate_cache()
        return _result(True, "Field updated")
    except Exception as exc:
        return _result(False, str(exc))


def delete_field(field_id):
    try:
        with _lock:
            conn = _connection()
            row = conn.execute("SELECT Name FROM dbo.Fields WHERE FieldId=?", field_id).fetchone()
            field_name = row[0] if row else f"Field #{field_id}"
            conn.execute("DELETE FROM dbo.Crops WHERE FieldId=?", field_id)
            conn.execute("DELETE FROM dbo.Fields WHERE FieldId=?", field_id)
            record_log(conn, "Delete Field", "Field", field_name, "Field and associated crops deleted")
            conn.commit()
            invalidate_cache()
        return _result(True, "Field and its crops deleted")
    except Exception as exc:
        return _result(False, str(exc))


def add_crop(field_id, name, variety, planting_date, expected_harvest, stage):
    try:
        with _lock:
            conn = _connection()
            conn.execute(
                "INSERT dbo.Crops (FieldId, Name, Variety, PlantingDate, ExpectedHarvestDate, GrowthStage) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                field_id, name, variety or None, planting_date, expected_harvest or None, stage,
            )
            detail = f"Planted {name} ({variety or 'Standard'}) - Stage: {stage}"
            record_log(conn, "Plant Crop", "Crop", name, detail)
            conn.commit()
            invalidate_cache()
        return _result(True, "Crop added")
    except Exception as exc:
        return _result(False, str(exc))


def update_crop(crop_id, field_id, name, variety, planting_date, expected_harvest, stage):
    try:
        with _lock:
            conn = _connection()
            conn.execute(
                "UPDATE dbo.Crops SET FieldId=?, Name=?, Variety=?, PlantingDate=?, ExpectedHarvestDate=?, "
                "GrowthStage=?, UpdatedAt=SYSUTCDATETIME() WHERE CropId=? AND IsArchived=0",
                field_id, name, variety or None, planting_date, expected_harvest or None, stage, crop_id,
            )
            detail = f"Updated {name} to stage: {stage}"
            record_log(conn, "Update Crop", "Crop", name, detail)
            conn.commit()
            invalidate_cache()
        return _result(True, "Crop updated")
    except Exception as exc:
        return _result(False, str(exc))


def delete_crop(crop_id):
    try:
        with _lock:
            conn = _connection()
            row = conn.execute("SELECT Name FROM dbo.Crops WHERE CropId=?", crop_id).fetchone()
            crop_name = row[0] if row else f"Crop #{crop_id}"
            conn.execute("DELETE FROM dbo.Crops WHERE CropId=?", crop_id)
            record_log(conn, "Delete Crop", "Crop", crop_name, "Crop record removed")
            conn.commit()
            invalidate_cache()
        return _result(True, "Crop deleted")
    except Exception as exc:
        return _result(False, str(exc))


def get_inventory():
    with _lock:
        if "inventory" in _cache:
            return list(_cache["inventory"])
        conn = _connection()
        rows = conn.execute(
            "SELECT i.InventoryItemId AS id, i.ItemName AS item_name, i.Category AS category, "
            "COALESCE(SUM(CASE WHEN t.TransactionType IN ('Opening','In','Adjustment') THEN t.Quantity "
            "WHEN t.TransactionType='Out' THEN -t.Quantity ELSE 0 END), 0) AS quantity, "
            "i.Unit AS unit, i.UpdatedAt AS last_updated "
            "FROM dbo.InventoryItems i LEFT JOIN dbo.InventoryTransactions t "
            "ON t.InventoryItemId=i.InventoryItemId WHERE i.IsArchived=0 "
            "GROUP BY i.InventoryItemId, i.ItemName, i.Category, i.Unit, i.UpdatedAt ORDER BY i.ItemName"
        ).fetchall()
        keys = ("id", "item_name", "category", "quantity", "unit", "last_updated")
        result = [dict(zip(keys, row)) for row in rows]
        _cache["inventory"] = result
        return list(result)


def add_inventory_item(item_name, category, quantity, unit):
    try:
        with _lock:
            conn = _connection()
            item_id = conn.execute(
                "INSERT dbo.InventoryItems (ItemName, Category, Unit) OUTPUT INSERTED.InventoryItemId VALUES (?, ?, ?)",
                item_name, category, unit,
            ).fetchone()[0]
            if quantity > 0:
                conn.execute(
                    "INSERT dbo.InventoryTransactions (InventoryItemId, TransactionType, Quantity, Notes) "
                    "VALUES (?, 'Opening', ?, 'Initial application entry')",
                    item_id, quantity,
                )
            record_log(conn, "Register Item", "Inventory", item_name, f"Registered under {category} with initial stock {quantity} {unit}")
            conn.commit()
            invalidate_cache()
        return _result(True, "Inventory item added")
    except Exception as exc:
        return _result(False, str(exc))


def adjust_inventory_stock(item_id, adjustment):
    try:
        try:
            adjustment = Decimal(str(adjustment))
        except (InvalidOperation, TypeError, ValueError):
            return _result(False, "Adjustment must be a valid number")
        if adjustment == 0:
            return _result(False, "Adjustment must be greater than zero")
        with _lock:
            conn = _connection()
            item_row = conn.execute("SELECT ItemName, Unit FROM dbo.InventoryItems WHERE InventoryItemId=?", item_id).fetchone()
            item_name = item_row[0] if item_row else f"Item #{item_id}"
            unit = item_row[1] if item_row else ""
            current = conn.execute(
                "SELECT COALESCE(SUM(CASE WHEN TransactionType IN ('Opening','In','Adjustment') THEN Quantity "
                "WHEN TransactionType='Out' THEN -Quantity ELSE 0 END), 0) "
                "FROM dbo.InventoryTransactions WHERE InventoryItemId=?",
                item_id,
            ).fetchone()[0]
            current_dec = Decimal(str(current))
            if current_dec + adjustment < 0:
                return _result(False, "Adjustment would make inventory negative")
            kind = "In" if adjustment >= 0 else "Out"
            conn.execute(
                "INSERT dbo.InventoryTransactions (InventoryItemId, TransactionType, Quantity, Notes) "
                "VALUES (?, ?, ?, 'Quick stock adjustment')",
                item_id, kind, abs(adjustment),
            )
            conn.execute("UPDATE dbo.InventoryItems SET UpdatedAt=SYSUTCDATETIME() WHERE InventoryItemId=?", item_id)
            sign = "+" if adjustment > 0 else ""
            record_log(conn, "Stock Adjustment", "Inventory", item_name, f"Stock adjusted by {sign}{adjustment} {unit}")
            conn.commit()
            invalidate_cache()
        return _result(True, "Inventory adjusted")
    except Exception as exc:
        return _result(False, str(exc))


def delete_inventory_item(item_id):
    try:
        with _lock:
            conn = _connection()
            row = conn.execute("SELECT ItemName FROM dbo.InventoryItems WHERE InventoryItemId=?", item_id).fetchone()
            item_name = row[0] if row else f"Item #{item_id}"
            conn.execute("DELETE FROM dbo.InventoryTransactions WHERE InventoryItemId=?", item_id)
            conn.execute("DELETE FROM dbo.InventoryItems WHERE InventoryItemId=?", item_id)
            record_log(conn, "Delete Item", "Inventory", item_name, "Inventory item removed")
            conn.commit()
            invalidate_cache()
        return _result(True, "Inventory item deleted")
    except Exception as exc:
        return _result(False, str(exc))


def get_dashboard_metrics(low_stock_threshold=10.0):
    cache_key = f"metrics_{low_stock_threshold}"
    with _lock:
        if cache_key in _cache:
            return dict(_cache[cache_key])
        conn = _connection()
        query = (
            "SELECT "
            "  (SELECT COUNT(*) FROM dbo.Fields WHERE IsArchived=0) AS total_fields, "
            "  (SELECT COALESCE(SUM(AreaAcres), 0) FROM dbo.Fields WHERE IsArchived=0) AS total_acres, "
            "  (SELECT COUNT(*) FROM dbo.Crops WHERE IsArchived=0 AND GrowthStage <> 'Harvested') AS active_crops, "
            "  (SELECT COUNT(*) FROM ("
            "     SELECT i.InventoryItemId "
            "     FROM dbo.InventoryItems i "
            "     LEFT JOIN dbo.InventoryTransactions t ON t.InventoryItemId=i.InventoryItemId "
            "     WHERE i.IsArchived=0 "
            "     GROUP BY i.InventoryItemId "
            "     HAVING COALESCE(SUM(CASE WHEN t.TransactionType IN ('Opening','In','Adjustment') THEN t.Quantity WHEN t.TransactionType='Out' THEN -t.Quantity ELSE 0 END), 0) < ?"
            "  ) q) AS low_stock_alerts"
        )
        row = conn.execute(query, low_stock_threshold).fetchone()
        res = {
            "total_fields": int(row[0] or 0),
            "total_acres": float(row[1] or 0.0),
            "active_crops": int(row[2] or 0),
            "low_stock_alerts": int(row[3] or 0)
        }
        _cache[cache_key] = res
        return dict(res)


def get_upcoming_activities(days=30):
    """Return crops whose harvest is due within the next *days* days or is already overdue
    but has not been marked as Harvested yet.  Results are sorted chronologically.

    Each row includes a ``harvest_status`` field:
      - "Overdue"  – harvest date is in the past, crop not yet harvested
      - "Today"    – harvest date is today
      - "Upcoming" – harvest date is in the future (within *days* days)
    """
    cache_key = f"upcoming_{days}"
    with _lock:
        if cache_key in _cache:
            return list(_cache[cache_key])
        conn = _connection()
        rows = conn.execute(
            "SELECT c.CropId AS id, c.Name AS crop_name, c.Variety AS variety, f.Name AS field_name, "
            "CONVERT(varchar(10), c.ExpectedHarvestDate, 23) AS expected_harvest, c.GrowthStage AS stage, "
            "CASE "
            "  WHEN c.ExpectedHarvestDate < CAST(GETDATE() AS date) THEN 'Overdue' "
            "  WHEN c.ExpectedHarvestDate = CAST(GETDATE() AS date) THEN 'Today' "
            "  ELSE 'Upcoming' "
            "END AS harvest_status "
            "FROM dbo.Crops c JOIN dbo.Fields f ON f.FieldId=c.FieldId "
            "WHERE c.IsArchived = 0 "
            "  AND c.ExpectedHarvestDate IS NOT NULL "
            "  AND c.GrowthStage <> 'Harvested' "
            "  AND c.ExpectedHarvestDate <= DATEADD(day, ?, CAST(GETDATE() AS date)) "
            "ORDER BY c.ExpectedHarvestDate",
            days,
        ).fetchall()
        keys = ("id", "crop_name", "variety", "field_name", "expected_harvest", "stage", "harvest_status")
        result = [dict(zip(keys, row)) for row in rows]
        _cache[cache_key] = result
        return list(result)
