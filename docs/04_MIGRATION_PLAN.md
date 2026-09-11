# SQLite to SQL Server Migration Plan

## Source

`_internal/farm_db.sqlite` is the source snapshot. It must be copied before every migration test.

## Target

- Server: `IT-Tauheed`
- Database: `AgriFarm`
- Authentication: Windows Authentication, verified for the current environment.

## Migration sequence

1. Validate source integrity and capture row counts/checksums.
2. Validate target connection and migration version.
3. Create target schema without dropping data.
4. Migrate fields and preserve source IDs where safe.
5. Migrate crops with translated field IDs.
6. Migrate inventory items and create opening balances.
7. Validate counts, relationships, quantities, and dates.
8. Commit only after all checks pass.
9. Produce a migration evidence report.

Every migration attempt must be transactional. A failed validation must roll back the target transaction and identify the exact failure.
