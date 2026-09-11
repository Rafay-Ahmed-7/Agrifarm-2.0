"""Migrate the legacy AgriFarm SQLite snapshot into SQL Server.

The command is dry-run by default. Use --apply only after reviewing the
validation output. The SQL Server transaction is rolled back on any failure.
"""

from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pyodbc


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SQLITE = ROOT / "_internal" / "farm_db.sqlite"
DEFAULT_SERVER = "IT-Tauheed"
DEFAULT_DATABASE = "AgriFarm"


@dataclass(frozen=True)
class SourceData:
    fields: list[tuple]
    crops: list[tuple]
    inventory: list[tuple]


def load_source(path: Path) -> SourceData:
    if not path.exists():
        raise FileNotFoundError(path)
    with sqlite3.connect(path) as conn:
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"SQLite integrity check failed: {integrity}")
        fields = conn.execute(
            "SELECT id, name, area_acres, soil_type, status FROM fields ORDER BY id"
        ).fetchall()
        crops = conn.execute(
            "SELECT id, field_id, name, variety, planting_date, expected_harvest, stage "
            "FROM crops ORDER BY id"
        ).fetchall()
        inventory = conn.execute(
            "SELECT id, item_name, category, quantity, unit, last_updated "
            "FROM inventory ORDER BY id"
        ).fetchall()
    return SourceData(fields, crops, inventory)


def validate_source(data: SourceData) -> None:
    field_ids = {row[0] for row in data.fields}
    field_names = [row[1] for row in data.fields]
    item_names = [row[1] for row in data.inventory]
    if len(field_names) != len(set(field_names)):
        raise ValueError("Duplicate field names in SQLite source")
    if len(item_names) != len(set(item_names)):
        raise ValueError("Duplicate inventory item names in SQLite source")
    for row in data.crops:
        if row[1] not in field_ids:
            raise ValueError(f"Crop {row[0]} references missing field {row[1]}")
        if row[5] and row[5] < row[4]:
            raise ValueError(f"Crop {row[0]} has harvest date before planting date")
    for row in data.inventory:
        if row[3] < 0:
            raise ValueError(f"Inventory item {row[0]} has negative quantity")


def connect(server: str, database: str) -> pyodbc.Connection:
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={server};DATABASE={database};"
        "Trusted_Connection=yes;TrustServerCertificate=yes;",
        autocommit=False,
    )


def target_counts(conn: pyodbc.Connection) -> dict[str, int]:
    cursor = conn.cursor()
    return {
        name: cursor.execute(f"SELECT COUNT(*) FROM dbo.{name}").fetchone()[0]
        for name in ("Fields", "Crops", "InventoryItems", "InventoryTransactions")
    }


def migrate(data: SourceData, conn: pyodbc.Connection) -> dict[str, int]:
    cursor = conn.cursor()
    before = target_counts(conn)
    if any(before[name] for name in ("Fields", "Crops", "InventoryItems", "InventoryTransactions")):
        raise RuntimeError(f"Target is not empty; refusing duplicate migration: {before}")

    try:
        cursor.execute("SET IDENTITY_INSERT dbo.Fields ON")
        cursor.fast_executemany = True
        cursor.executemany(
            "INSERT dbo.Fields (FieldId, Name, AreaAcres, SoilType, Status) VALUES (?, ?, ?, ?, ?)",
            data.fields,
        )
        cursor.execute("SET IDENTITY_INSERT dbo.Fields OFF")

        cursor.execute("SET IDENTITY_INSERT dbo.Crops ON")
        cursor.executemany(
            "INSERT dbo.Crops (CropId, FieldId, Name, Variety, PlantingDate, ExpectedHarvestDate, GrowthStage) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            data.crops,
        )
        cursor.execute("SET IDENTITY_INSERT dbo.Crops OFF")

        cursor.execute("SET IDENTITY_INSERT dbo.InventoryItems ON")
        cursor.executemany(
            "INSERT dbo.InventoryItems (InventoryItemId, ItemName, Category, Unit, UpdatedAt) "
            "VALUES (?, ?, ?, ?, ?)",
            [(row[0], row[1], row[2], row[4], row[5]) for row in data.inventory],
        )
        cursor.execute("SET IDENTITY_INSERT dbo.InventoryItems OFF")

        cursor.fast_executemany = True
        cursor.executemany(
            "INSERT dbo.InventoryTransactions (InventoryItemId, TransactionType, Quantity, Notes) "
            "VALUES (?, N'Opening', ?, N'Migrated from SQLite farm_db.sqlite')",
            [(row[0], row[3]) for row in data.inventory if row[3] > 0],
        )

        after = target_counts(conn)
        expected = {
            "Fields": len(data.fields),
            "Crops": len(data.crops),
            "InventoryItems": len(data.inventory),
            "InventoryTransactions": sum(row[3] > 0 for row in data.inventory),
        }
        if after != expected:
            raise RuntimeError(f"Target validation failed: expected {expected}, got {after}")
        return after
    except Exception:
        conn.rollback()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sqlite", type=Path, default=DEFAULT_SQLITE)
    parser.add_argument("--server", default=DEFAULT_SERVER)
    parser.add_argument("--database", default=DEFAULT_DATABASE)
    parser.add_argument("--apply", action="store_true", help="commit the migration")
    args = parser.parse_args()

    data = load_source(args.sqlite)
    validate_source(data)
    print(f"Source validated at {datetime.now().isoformat(timespec='seconds')}")
    print(f"Source counts: fields={len(data.fields)}, crops={len(data.crops)}, inventory={len(data.inventory)}")
    if not args.apply:
        print("DRY RUN: no SQL Server changes were made")
        return 0

    conn = connect(args.server, args.database)
    try:
        counts = migrate(data, conn)
        conn.commit()
        print(f"COMMITTED: {counts}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
