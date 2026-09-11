# Data Mapping

| SQLite source | SQL Server target | Notes |
|---|---|---|
| `fields.id` | `dbo.Fields.FieldId` | Preserve IDs where possible |
| `fields.name` | `dbo.Fields.Name` | Unique, required |
| `fields.area_acres` | `dbo.Fields.AreaAcres` | Positive decimal |
| `fields.soil_type` | `dbo.Fields.SoilType` | Nullable text |
| `fields.status` | `dbo.Fields.Status` | Constrained value |
| `crops.id` | `dbo.Crops.CropId` | Preserve IDs where possible |
| `crops.field_id` | `dbo.Crops.FieldId` | Foreign-key translation |
| `crops.name` | `dbo.Crops.Name` | Required |
| `crops.variety` | `dbo.Crops.Variety` | Nullable text |
| `crops.planting_date` | `dbo.Crops.PlantingDate` | Convert to `date` |
| `crops.expected_harvest` | `dbo.Crops.ExpectedHarvestDate` | Convert to `date` |
| `crops.stage` | `dbo.Crops.GrowthStage` | Constrained value |
| `inventory.id` | `dbo.InventoryItems.InventoryItemId` | Preserve IDs where possible |
| `inventory.item_name` | `dbo.InventoryItems.ItemName` | Unique, required |
| `inventory.category` | `dbo.InventoryItems.Category` | Constrained value |
| `inventory.quantity` | opening transaction/current compatibility balance | No quantity loss |
| `inventory.unit` | `dbo.InventoryItems.Unit` | Required |
| `inventory.last_updated` | `dbo.InventoryItems.UpdatedAt` | Convert to `datetime2` |
