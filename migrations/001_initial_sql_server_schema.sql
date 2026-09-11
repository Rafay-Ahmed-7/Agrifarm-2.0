USE [AgriFarm];
GO

IF OBJECT_ID(N'dbo.SchemaMigrations', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.SchemaMigrations
    (
        MigrationId  nvarchar(100) NOT NULL CONSTRAINT PK_SchemaMigrations PRIMARY KEY,
        AppliedAt    datetime2(0) NOT NULL CONSTRAINT DF_SchemaMigrations_AppliedAt DEFAULT SYSUTCDATETIME()
    );
END;
GO

IF OBJECT_ID(N'dbo.Fields', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Fields
    (
        FieldId     int IDENTITY(1,1) NOT NULL CONSTRAINT PK_Fields PRIMARY KEY,
        Name        nvarchar(200) NOT NULL,
        AreaAcres   decimal(12,2) NOT NULL,
        SoilType    nvarchar(100) NULL,
        Status      nvarchar(20) NOT NULL,
        CreatedAt   datetime2(0) NOT NULL CONSTRAINT DF_Fields_CreatedAt DEFAULT SYSUTCDATETIME(),
        UpdatedAt   datetime2(0) NOT NULL CONSTRAINT DF_Fields_UpdatedAt DEFAULT SYSUTCDATETIME(),
        IsArchived  bit NOT NULL CONSTRAINT DF_Fields_IsArchived DEFAULT 0,
        CONSTRAINT UQ_Fields_Name UNIQUE (Name),
        CONSTRAINT CK_Fields_AreaAcres_Positive CHECK (AreaAcres > 0),
        CONSTRAINT CK_Fields_Status CHECK (Status IN (N'Active', N'Fallow', N'Resting'))
    );
END;
GO

IF OBJECT_ID(N'dbo.Crops', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Crops
    (
        CropId               int IDENTITY(1,1) NOT NULL CONSTRAINT PK_Crops PRIMARY KEY,
        FieldId              int NOT NULL,
        Name                 nvarchar(200) NOT NULL,
        Variety              nvarchar(200) NULL,
        PlantingDate         date NOT NULL,
        ExpectedHarvestDate  date NULL,
        GrowthStage          nvarchar(30) NOT NULL,
        CreatedAt            datetime2(0) NOT NULL CONSTRAINT DF_Crops_CreatedAt DEFAULT SYSUTCDATETIME(),
        UpdatedAt            datetime2(0) NOT NULL CONSTRAINT DF_Crops_UpdatedAt DEFAULT SYSUTCDATETIME(),
        IsArchived           bit NOT NULL CONSTRAINT DF_Crops_IsArchived DEFAULT 0,
        CONSTRAINT FK_Crops_Fields FOREIGN KEY (FieldId) REFERENCES dbo.Fields(FieldId),
        CONSTRAINT CK_Crops_Dates CHECK (ExpectedHarvestDate IS NULL OR ExpectedHarvestDate >= PlantingDate),
        CONSTRAINT CK_Crops_GrowthStage CHECK (GrowthStage IN (N'Seedling', N'Vegetative', N'Flowering', N'Harvest-Ready', N'Harvested'))
    );
END;
GO

IF OBJECT_ID(N'dbo.InventoryItems', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.InventoryItems
    (
        InventoryItemId  int IDENTITY(1,1) NOT NULL CONSTRAINT PK_InventoryItems PRIMARY KEY,
        ItemName         nvarchar(200) NOT NULL,
        Category         nvarchar(30) NOT NULL,
        Unit             nvarchar(50) NOT NULL,
        ReorderLevel     decimal(18,3) NOT NULL CONSTRAINT DF_InventoryItems_ReorderLevel DEFAULT 10.0,
        CreatedAt        datetime2(0) NOT NULL CONSTRAINT DF_InventoryItems_CreatedAt DEFAULT SYSUTCDATETIME(),
        UpdatedAt        datetime2(0) NOT NULL CONSTRAINT DF_InventoryItems_UpdatedAt DEFAULT SYSUTCDATETIME(),
        IsArchived       bit NOT NULL CONSTRAINT DF_InventoryItems_IsArchived DEFAULT 0,
        CONSTRAINT UQ_InventoryItems_ItemName UNIQUE (ItemName),
        CONSTRAINT CK_InventoryItems_Category CHECK (Category IN (N'Seeds', N'Fertilizer', N'Pesticide', N'Tools')),
        CONSTRAINT CK_InventoryItems_ReorderLevel_NonNegative CHECK (ReorderLevel >= 0)
    );
END;
GO

IF OBJECT_ID(N'dbo.InventoryTransactions', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.InventoryTransactions
    (
        InventoryTransactionId  bigint IDENTITY(1,1) NOT NULL CONSTRAINT PK_InventoryTransactions PRIMARY KEY,
        InventoryItemId        int NOT NULL,
        TransactionType         nvarchar(20) NOT NULL,
        Quantity                decimal(18,3) NOT NULL,
        TransactionDate         datetime2(0) NOT NULL CONSTRAINT DF_InventoryTransactions_TransactionDate DEFAULT SYSUTCDATETIME(),
        Notes                   nvarchar(500) NULL,
        CONSTRAINT FK_InventoryTransactions_Items FOREIGN KEY (InventoryItemId) REFERENCES dbo.InventoryItems(InventoryItemId),
        CONSTRAINT CK_InventoryTransactions_Type CHECK (TransactionType IN (N'Opening', N'In', N'Out', N'Adjustment')),
        CONSTRAINT CK_InventoryTransactions_Quantity_Positive CHECK (Quantity > 0)
    );
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.SchemaMigrations WHERE MigrationId = N'001_initial_sql_server_schema')
BEGIN
    INSERT dbo.SchemaMigrations (MigrationId) VALUES (N'001_initial_sql_server_schema');
END;
GO
