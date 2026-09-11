# AgriFarm SQL Server Target Architecture

```text
CustomTkinter views
        -> application services
        -> repository/data-access layer
        -> SQL Server (authoritative)
```

SQLite is retained only as the historical migration source and backup reference. The renovated application must not silently fall back to SQLite.

## Initial migration scope

1. Preserve fields, crops, and inventory behavior.
2. Move persistence to SQL Server.
3. Add explicit transactions, rollback, validation, and diagnostics.
4. Keep UI redesign and new modules behind the persistence verification gate.

## Future extensions

- Inventory transaction ledger.
- Crop activities and harvest records.
- Users, roles, and audit history.
- Reports and exports.
- Automated backups and migrations.
