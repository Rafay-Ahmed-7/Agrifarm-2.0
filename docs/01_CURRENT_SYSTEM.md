# AgriFarm Current System

## Verified baseline

- Distribution: packaged Windows CustomTkinter application.
- Executable: `AgriFarm.exe`.
- Current data store: `_internal/farm_db.sqlite`.
- Current SQLite tables: `fields`, `crops`, `inventory`.
- Current database integrity: `ok`.
- Current sample data: 3 fields, 2 crops, 5 inventory items.
- No application source entrypoint, database module, logger module, or build configuration is present in the package; UI view/widget modules are present.

## Current workflows

- Dashboard metrics and upcoming harvests.
- Field CRUD.
- Crop CRUD linked to fields.
- Inventory item registration, adjustment, and deletion.
- Settings database diagnostics and theme selection.

## Preservation rule

The existing executable and SQLite database are treated as the rollback/reference baseline. Migration work must not overwrite either artifact.
