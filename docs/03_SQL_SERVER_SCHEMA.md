# SQL Server Schema Plan

## Initial tables

### `dbo.Fields`

Stores farm field definitions. `Name` is unique. `Status` is constrained to `Active`, `Fallow`, or `Resting`.

### `dbo.Crops`

Stores cultivated crops and references `dbo.Fields(FieldId)`. Crop deletion behavior must be approved before implementation; archival is preferred over destructive deletion.

### `dbo.InventoryItems`

Stores inventory item identity, category, unit, reorder level, and opening/current balance during the compatibility stage.

### `dbo.InventoryTransactions` (recommended next step)

Stores stock-in and stock-out movements. Current balance is derived from the ledger. Existing SQLite quantities become opening-balance transactions.

## Required constraints

- Primary keys and foreign keys.
- Unique field and inventory names.
- Valid status/category/stage values.
- Positive field area.
- Non-negative stock quantities.
- Harvest date not earlier than planting date.
- Created/updated timestamps.

The final SQL script must be idempotent or versioned through migrations and must not drop existing user data.
