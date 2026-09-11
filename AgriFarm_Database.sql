IF DB_ID(N'AgriFarm') IS NULL
    CREATE DATABASE AgriFarm;
GO

USE [AgriFarm];
GO

-- Drop existing tables in reverse dependency order
IF OBJECT_ID(N'dbo.InventoryTransactions', N'U') IS NOT NULL DROP TABLE dbo.[InventoryTransactions];
IF OBJECT_ID(N'dbo.Crops', N'U') IS NOT NULL DROP TABLE dbo.[Crops];
IF OBJECT_ID(N'dbo.InventoryItems', N'U') IS NOT NULL DROP TABLE dbo.[InventoryItems];
IF OBJECT_ID(N'dbo.Fields', N'U') IS NOT NULL DROP TABLE dbo.[Fields];
IF OBJECT_ID(N'dbo.SchemaMigrations', N'U') IS NOT NULL DROP TABLE dbo.[SchemaMigrations];
GO

-- ============================================================
-- Table: dbo.Fields
-- ============================================================

CREATE TABLE dbo.[Fields] (
    [FieldId] int IDENTITY(1,1) NOT NULL,
    [Name] nvarchar(200) NOT NULL,
    [AreaAcres] decimal(12,2) NOT NULL,
    [SoilType] nvarchar(100) NULL,
    [Status] nvarchar(20) NOT NULL,
    [CreatedAt] datetime2(0) NOT NULL,
    [UpdatedAt] datetime2(0) NOT NULL,
    [IsArchived] bit NOT NULL,
    CONSTRAINT [PK_Fields] PRIMARY KEY ([FieldId]),
    CONSTRAINT [CK_Fields_AreaAcres_Positive] CHECK ([AreaAcres]>(0)),
    CONSTRAINT [CK_Fields_Status] CHECK ([Status]=N'Resting' OR [Status]=N'Fallow' OR [Status]=N'Active')
);
GO

-- ============================================================
-- Table: dbo.Crops
-- ============================================================

CREATE TABLE dbo.[Crops] (
    [CropId] int IDENTITY(1,1) NOT NULL,
    [FieldId] int NOT NULL,
    [Name] nvarchar(200) NOT NULL,
    [Variety] nvarchar(200) NULL,
    [PlantingDate] date NOT NULL,
    [ExpectedHarvestDate] date NULL,
    [GrowthStage] nvarchar(30) NOT NULL,
    [CreatedAt] datetime2(0) NOT NULL,
    [UpdatedAt] datetime2(0) NOT NULL,
    [IsArchived] bit NOT NULL,
    CONSTRAINT [PK_Crops] PRIMARY KEY ([CropId]),
    CONSTRAINT [FK_Crops_Fields] FOREIGN KEY ([FieldId]) REFERENCES dbo.[Fields]([FieldId]),
    CONSTRAINT [CK_Crops_Dates] CHECK ([ExpectedHarvestDate] IS NULL OR [ExpectedHarvestDate]>=[PlantingDate]),
    CONSTRAINT [CK_Crops_GrowthStage] CHECK ([GrowthStage]=N'Harvested' OR [GrowthStage]=N'Harvest-Ready' OR [GrowthStage]=N'Flowering' OR [GrowthStage]=N'Vegetative' OR [GrowthStage]=N'Seedling')
);
GO

-- ============================================================
-- Table: dbo.InventoryItems
-- ============================================================

CREATE TABLE dbo.[InventoryItems] (
    [InventoryItemId] int IDENTITY(1,1) NOT NULL,
    [ItemName] nvarchar(200) NOT NULL,
    [Category] nvarchar(30) NOT NULL,
    [Unit] nvarchar(50) NOT NULL,
    [ReorderLevel] decimal(18,3) NOT NULL,
    [CreatedAt] datetime2(0) NOT NULL,
    [UpdatedAt] datetime2(0) NOT NULL,
    [IsArchived] bit NOT NULL,
    CONSTRAINT [PK_InventoryItems] PRIMARY KEY ([InventoryItemId]),
    CONSTRAINT [CK_InventoryItems_Category] CHECK ([Category]=N'Tools' OR [Category]=N'Pesticide' OR [Category]=N'Fertilizer' OR [Category]=N'Seeds'),
    CONSTRAINT [CK_InventoryItems_ReorderLevel_NonNegative] CHECK ([ReorderLevel]>=(0))
);
GO

-- ============================================================
-- Table: dbo.InventoryTransactions
-- ============================================================

CREATE TABLE dbo.[InventoryTransactions] (
    [InventoryTransactionId] bigint IDENTITY(1,1) NOT NULL,
    [InventoryItemId] int NOT NULL,
    [TransactionType] nvarchar(20) NOT NULL,
    [Quantity] decimal(18,3) NOT NULL,
    [TransactionDate] datetime2(0) NOT NULL,
    [Notes] nvarchar(500) NULL,
    CONSTRAINT [PK_InventoryTransactions] PRIMARY KEY ([InventoryTransactionId]),
    CONSTRAINT [FK_InventoryTransactions_Items] FOREIGN KEY ([InventoryItemId]) REFERENCES dbo.[InventoryItems]([InventoryItemId]),
    CONSTRAINT [CK_InventoryTransactions_Quantity_Positive] CHECK ([Quantity]>(0)),
    CONSTRAINT [CK_InventoryTransactions_Type] CHECK ([TransactionType]=N'Adjustment' OR [TransactionType]=N'Out' OR [TransactionType]=N'In' OR [TransactionType]=N'Opening')
);
GO

-- ============================================================
-- Table: dbo.SchemaMigrations
-- ============================================================

CREATE TABLE dbo.[SchemaMigrations] (
    [MigrationId] nvarchar(100) NOT NULL,
    [AppliedAt] datetime2(0) NOT NULL,
    CONSTRAINT [PK_SchemaMigrations] PRIMARY KEY ([MigrationId])
);
GO


-- ============================================================
-- DATA
-- ============================================================

-- Fields: 7 rows
SET IDENTITY_INSERT dbo.[Fields] ON;
INSERT INTO dbo.[Fields] ([FieldId], [Name], [AreaAcres], [SoilType], [Status], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (1, N'North Meadow', 12.50, N'Clay Loam', N'Active', '2026-09-09 14:37:33', '2026-09-09 14:37:33', 0);
INSERT INTO dbo.[Fields] ([FieldId], [Name], [AreaAcres], [SoilType], [Status], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (3, N'East Field', 15.00, N'Silt Loam', N'Fallow', '2026-09-09 14:37:33', '2026-09-11 14:28:20', 0);
INSERT INTO dbo.[Fields] ([FieldId], [Name], [AreaAcres], [SoilType], [Status], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (7, N'TubeWell Side', 16.00, N'Clay Loam', N'Resting', '2026-09-09 14:44:48', '2026-09-11 14:28:29', 0);
INSERT INTO dbo.[Fields] ([FieldId], [Name], [AreaAcres], [SoilType], [Status], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (16, N'South Orchard', 8.75, N'Sandy Loam', N'Active', '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[Fields] ([FieldId], [Name], [AreaAcres], [SoilType], [Status], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (17, N'West Paddock', 20.00, N'Clay', N'Resting', '2026-09-09 17:43:30', '2026-09-11 14:28:45', 0);
INSERT INTO dbo.[Fields] ([FieldId], [Name], [AreaAcres], [SoilType], [Status], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (18, N'River Bend', 11.25, N'Alluvial', N'Active', '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[Fields] ([FieldId], [Name], [AreaAcres], [SoilType], [Status], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (19, N'Greenhouse A', 1.50, N'Peat Mix', N'Active', '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
SET IDENTITY_INSERT dbo.[Fields] OFF;

-- Crops: 16 rows
SET IDENTITY_INSERT dbo.[Crops] ON;
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (3, 7, N'Rice', N'Basmati', '2026-09-09', '2027-01-02', N'Seedling', '2026-09-09 14:45:39', '2026-09-09 14:46:04', 0);
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (6, 1, N'Corn', N'Sweet Yellow', '2026-05-06', '2026-09-03', N'Vegetative', '2026-09-09 14:54:45', '2026-09-09 14:54:45', 0);
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (16, 7, N'Rice', N'Basmati', '2026-09-09', '2026-10-02', N'Seedling', '2026-09-09 17:37:55', '2026-09-09 17:37:55', 0);
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (18, 18, N'Sunflower', N'Hysun 33', '2026-06-11', '2026-09-21', N'Flowering', '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (22, 18, N'Soybean', N'JS 335', '2026-07-01', '2026-10-04', N'Flowering', '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (24, 19, N'Tomato', N'Roma VF', '2026-08-20', '2026-11-13', N'Seedling', '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (25, 3, N'Garlic', N'White Garlic', '2026-08-10', '2027-02-06', N'Vegetative', '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (26, 1, N'Potato', N'Cardinal', '2026-08-25', '2026-11-23', N'Vegetative', '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (27, 19, N'Onion', N'Red Creole', '2026-08-30', '2026-12-08', N'Seedling', '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (28, 3, N'Mustard', N'BARI Sharisha-14', '2026-05-12', '2026-08-15', N'Harvested', '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (29, 1, N'Lentil', N'Masoor Local', '2026-05-02', '2026-08-10', N'Harvested', '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (30, 17, N'Wheat', N'HD-2967', '2026-05-22', '2026-09-04', N'Harvest-Ready', '2026-09-09 17:44:22', '2026-09-09 17:44:22', 0);
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (31, 3, N'Chickpea', N'Kabuli Large', '2026-06-06', '2026-09-17', N'Harvest-Ready', '2026-09-09 17:44:22', '2026-09-09 17:44:22', 0);
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (32, 17, N'Cotton', N'Bt Cotton Hybrid', '2026-07-11', '2026-11-03', N'Flowering', '2026-09-09 17:44:22', '2026-09-09 17:44:22', 0);
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (33, 16, N'Sugarcane', N'Co 238', '2026-03-13', '2026-12-08', N'Vegetative', '2026-09-09 17:44:22', '2026-09-09 17:44:22', 0);
INSERT INTO dbo.[Crops] ([CropId], [FieldId], [Name], [Variety], [PlantingDate], [ExpectedHarvestDate], [GrowthStage], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (34, 16, N'Mango', N'Chaunsa', '2025-09-09', '2026-09-29', N'Harvest-Ready', '2026-09-09 17:44:22', '2026-09-09 17:44:22', 0);
SET IDENTITY_INSERT dbo.[Crops] OFF;

-- InventoryItems: 29 rows
SET IDENTITY_INSERT dbo.[InventoryItems] ON;
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (1, N'Organic Nitrogen Fertilizer', N'Fertilizer', N'kg', 10.000, '2026-09-09 14:37:33', '2026-06-04 19:46:41', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (2, N'Tomato Hybrid Seeds', N'Seeds', N'kg', 10.000, '2026-09-09 14:37:33', '2026-06-04 19:46:41', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (3, N'Broad Spectrum Fungicide', N'Pesticide', N'liters', 10.000, '2026-09-09 14:37:33', '2026-09-09 15:04:35', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (4, N'Heavy Duty Rakes', N'Tools', N'units', 10.000, '2026-09-09 14:37:33', '2026-06-04 19:46:41', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (5, N'Drip Irrigation Hose 100m', N'Tools', N'units', 10.000, '2026-09-09 14:37:33', '2026-09-09 15:35:01', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (11, N'DAP Fertilizer', N'Fertilizer', N'kg', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (12, N'Urea (46% N)', N'Fertilizer', N'kg', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (13, N'Potassium Sulphate', N'Fertilizer', N'kg', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (14, N'Organic Compost', N'Fertilizer', N'kg', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (15, N'Boron Micronutrient', N'Fertilizer', N'kg', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (16, N'Zinc Sulphate', N'Fertilizer', N'kg', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (17, N'Wheat Certified Seeds', N'Seeds', N'kg', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (18, N'Sunflower Hybrid Seeds', N'Seeds', N'kg', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (19, N'Cotton Bt Seeds', N'Seeds', N'kg', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (20, N'Vegetable Seed Mix', N'Seeds', N'kg', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (21, N'Imidacloprid Insecticide', N'Pesticide', N'liters', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (22, N'Glyphosate Herbicide', N'Pesticide', N'liters', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (23, N'Chlorpyrifos EC', N'Pesticide', N'liters', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (24, N'Copper Oxychloride', N'Pesticide', N'kg', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (25, N'Mancozeb WP', N'Pesticide', N'kg', 10.000, '2026-09-09 17:43:30', '2026-09-11 14:29:45', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (26, N'Knapsack Sprayer 16L', N'Tools', N'units', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (27, N'Shovel & Spade Set', N'Tools', N'units', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (28, N'Irrigation Pipe 50m', N'Tools', N'units', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (29, N'Garden Gloves (pairs)', N'Tools', N'units', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (30, N'Pruning Shears', N'Tools', N'units', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (31, N'Wheelbarrow', N'Tools', N'units', 10.000, '2026-09-09 17:43:30', '2026-09-09 17:43:30', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (36, N'Diesel Fuel (20L Jerrycan)', N'Tools', N'liters', 10.000, '2026-09-09 17:44:22', '2026-09-09 17:44:22', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (37, N'Engine Oil 20W-50', N'Tools', N'liters', 10.000, '2026-09-09 17:44:22', '2026-09-09 17:44:22', 0);
INSERT INTO dbo.[InventoryItems] ([InventoryItemId], [ItemName], [Category], [Unit], [ReorderLevel], [CreatedAt], [UpdatedAt], [IsArchived]) VALUES (39, N'Jute Harvest Sacks', N'Tools', N'units', 10.000, '2026-09-09 17:44:22', '2026-09-09 17:44:22', 0);
SET IDENTITY_INSERT dbo.[InventoryItems] OFF;

-- InventoryTransactions: 35 rows
SET IDENTITY_INSERT dbo.[InventoryTransactions] ON;
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (1, 1, N'Opening', 45.000, '2026-09-09 14:37:33', N'Migrated from SQLite farm_db.sqlite');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (2, 2, N'Opening', 5.000, '2026-09-09 14:37:33', N'Migrated from SQLite farm_db.sqlite');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (3, 3, N'Opening', 12.500, '2026-09-09 14:37:33', N'Migrated from SQLite farm_db.sqlite');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (4, 4, N'Opening', 8.000, '2026-09-09 14:37:33', N'Migrated from SQLite farm_db.sqlite');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (5, 5, N'Opening', 3.000, '2026-09-09 14:37:33', N'Migrated from SQLite farm_db.sqlite');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (14, 5, N'In', 5.000, '2026-09-09 14:54:29', N'Quick stock adjustment');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (15, 3, N'In', 1.000, '2026-09-09 15:04:35', N'Quick stock adjustment');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (16, 3, N'Out', 1.000, '2026-09-09 15:04:35', N'Quick stock adjustment');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (20, 5, N'In', 5.000, '2026-09-09 15:35:01', N'Quick stock adjustment');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (24, 11, N'Opening', 120.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (25, 12, N'Opening', 200.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (26, 13, N'Opening', 75.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (27, 14, N'Opening', 500.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (28, 15, N'Opening', 8.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (29, 16, N'Opening', 15.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (30, 17, N'Opening', 180.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (31, 18, N'Opening', 4.500, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (32, 19, N'Opening', 22.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (33, 20, N'Opening', 3.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (34, 21, N'Opening', 18.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (35, 22, N'Opening', 25.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (36, 23, N'Opening', 6.500, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (37, 24, N'Opening', 12.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (38, 25, N'Opening', 9.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (39, 26, N'Opening', 4.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (40, 27, N'Opening', 6.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (41, 28, N'Opening', 10.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (42, 29, N'Opening', 20.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (43, 30, N'Opening', 8.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (44, 31, N'Opening', 3.000, '2026-09-09 17:43:30', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (45, 36, N'Opening', 150.000, '2026-09-09 17:44:22', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (46, 37, N'Opening', 12.000, '2026-09-09 17:44:22', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (48, 39, N'Opening', 200.000, '2026-09-09 17:44:22', N'Initial application entry');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (51, 25, N'Out', 9.000, '2026-09-11 14:29:39', N'Quick stock adjustment');
INSERT INTO dbo.[InventoryTransactions] ([InventoryTransactionId], [InventoryItemId], [TransactionType], [Quantity], [TransactionDate], [Notes]) VALUES (52, 25, N'In', 10.000, '2026-09-11 14:29:45', N'Quick stock adjustment');
SET IDENTITY_INSERT dbo.[InventoryTransactions] OFF;

-- SchemaMigrations: 1 rows
INSERT INTO dbo.[SchemaMigrations] ([MigrationId], [AppliedAt]) VALUES (N'001_initial_sql_server_schema', '2026-09-08 18:20:36');

-- 1. View all Fields (Land plots, area in acres, soil type, and status)
SELECT * FROM dbo.Fields;

-- 2. View all Crops (Planting date, harvest date, growth stage, linked FieldId)
SELECT * FROM dbo.Crops;

-- 3. View all Inventory Items (Name, Category, Unit, Reorder Level)
SELECT * FROM dbo.InventoryItems;

-- 4. View all Inventory Transactions (Stock In/Out ledger records with timestamps)
SELECT * FROM dbo.InventoryTransactions;

-- 5. View Database Migration History
SELECT * FROM dbo.SchemaMigrations;

SELECT 
    c.CropId,
    c.Name AS CropName,
    c.Variety,
    c.GrowthStage,
    c.PlantingDate,
    c.ExpectedHarvestDate,
    f.Name AS FieldName,
    f.AreaAcres,
    f.SoilType
FROM dbo.Crops c
INNER JOIN dbo.Fields f ON c.FieldId = f.FieldId
WHERE c.IsArchived = 0
ORDER BY c.PlantingDate DESC;

USE [AgriFarm];
GO

SELECT 
    i.InventoryItemId,
    i.ItemName,
    i.Category,
    i.Unit,
    i.ReorderLevel,
    COALESCE(SUM(CASE 
        WHEN t.TransactionType IN ('In', 'Opening') THEN t.Quantity
        WHEN t.TransactionType = 'Out' THEN -t.Quantity
        ELSE 0 
    END), 0) AS CurrentStock,
    CASE 
        WHEN COALESCE(SUM(CASE 
            WHEN t.TransactionType IN ('In', 'Opening') THEN t.Quantity
            WHEN t.TransactionType = 'Out' THEN -t.Quantity
            ELSE 0 
        END), 0) <= i.ReorderLevel THEN 'REORDER NEEDED'
        ELSE 'Sufficient'
    END AS StockStatus
FROM dbo.InventoryItems i
LEFT JOIN dbo.InventoryTransactions t ON i.InventoryItemId = t.InventoryItemId
WHERE i.IsArchived = 0
GROUP BY i.InventoryItemId, i.ItemName, i.Category, i.Unit, i.ReorderLevel
ORDER BY i.Category, i.ItemName;

USE [AgriFarm];
GO

SELECT 
    f.FieldId,
    f.Name AS FieldName,
    f.AreaAcres,
    f.Status AS FieldStatus,
    COUNT(c.CropId) AS TotalCropsPlanted
FROM dbo.Fields f
LEFT JOIN dbo.Crops c ON f.FieldId = c.FieldId AND c.IsArchived = 0
WHERE f.IsArchived = 0
GROUP BY f.FieldId, f.Name, f.AreaAcres, f.Status
ORDER BY f.AreaAcres DESC;


GO