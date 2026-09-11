# SQL Server Migration Acceptance Plan

## Persistence

- Add a field through the application and verify it in SQL Server.
- Restart the application and verify the record remains.
- Add and edit a crop linked to that field.
- Adjust inventory and verify the resulting balance.

## Integrity

- Source and target row counts match.
- Every crop references an existing field.
- Inventory quantities and units are preserved.
- Invalid status, category, dates, and negative quantities are rejected.

## Transaction safety

- Inject a migration failure.
- Confirm no partial migration remains.
- Verify rollback evidence in the migration report.

## Failure behavior

- Run with SQL Server unavailable.
- Confirm the application shows a clear connection error.
- Confirm it does not display fabricated or stale success data.

Completion requires criterion-level evidence, not merely source presence or unit-test success.
