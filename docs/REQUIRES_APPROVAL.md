# Decisions Requiring Approval

These decisions are intentionally recorded rather than silently assumed.

| Decision | Current recommendation | Status |
|---|---|---|
| SQL Server authority | SQL Server authoritative; no SQLite fallback | Proposed |
| Server/database | `IT-Tauheed` / `AgriFarm` | Verified environment |
| Authentication | Windows Authentication | Verified environment |
| Field deletion | Archive instead of permanent delete | Awaiting approval |
| Inventory model | Add transaction ledger after compatibility migration | Proposed |
| User accounts/roles | Defer until persistence migration is stable | Proposed |
| Sample records | Preserve in migration test; decide separately for production | Awaiting approval |
| ID preservation | Preserve existing IDs where possible | Proposed |
