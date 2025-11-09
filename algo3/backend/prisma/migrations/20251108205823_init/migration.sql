-- CreateTable
CREATE TABLE "products" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "sku" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "price" REAL NOT NULL,
    "stock" INTEGER NOT NULL DEFAULT 0,
    "rotation" TEXT NOT NULL DEFAULT 'low',
    "image_url" TEXT,
    "last_sold" DATETIME,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME NOT NULL
);

-- CreateTable
CREATE TABLE "channels" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "type" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'disconnected',
    "last_sync" DATETIME,
    "credentials" JSONB,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME NOT NULL
);

-- CreateTable
CREATE TABLE "product_channels" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "product_id" TEXT NOT NULL,
    "channel_id" TEXT NOT NULL,
    "external_id" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'active',
    "synced_at" DATETIME,
    CONSTRAINT "product_channels_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "products" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT "product_channels_channel_id_fkey" FOREIGN KEY ("channel_id") REFERENCES "channels" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "recommendations" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "type" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "summary" TEXT NOT NULL,
    "details" JSONB,
    "severity" TEXT NOT NULL DEFAULT 'medium',
    "confidence" REAL NOT NULL DEFAULT 0.5,
    "impact_est" JSONB,
    "status" TEXT NOT NULL DEFAULT 'pending',
    "product_id" TEXT,
    "applied_at" DATETIME,
    "expires_at" DATETIME,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" DATETIME NOT NULL,
    CONSTRAINT "recommendations_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "products" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "analysis_cache" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "cache_key" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "product_sku" TEXT,
    "result" JSONB NOT NULL,
    "confidence" REAL NOT NULL DEFAULT 0.5,
    "metadata" JSONB,
    "expires_at" DATETIME NOT NULL,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "ai_usage" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "model" TEXT NOT NULL,
    "operation" TEXT NOT NULL,
    "prompt_tokens" INTEGER NOT NULL,
    "completion_tokens" INTEGER NOT NULL,
    "total_tokens" INTEGER NOT NULL,
    "cost" REAL NOT NULL DEFAULT 0.0,
    "duration" INTEGER NOT NULL,
    "success" BOOLEAN NOT NULL DEFAULT true,
    "error_message" TEXT,
    "metadata" JSONB,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateIndex
CREATE UNIQUE INDEX "products_sku_key" ON "products"("sku");

-- CreateIndex
CREATE UNIQUE INDEX "product_channels_product_id_channel_id_key" ON "product_channels"("product_id", "channel_id");

-- CreateIndex
CREATE UNIQUE INDEX "analysis_cache_cache_key_key" ON "analysis_cache"("cache_key");

-- CreateIndex
CREATE INDEX "analysis_cache_product_sku_idx" ON "analysis_cache"("product_sku");

-- CreateIndex
CREATE INDEX "analysis_cache_expires_at_idx" ON "analysis_cache"("expires_at");

-- CreateIndex
CREATE INDEX "ai_usage_created_at_idx" ON "ai_usage"("created_at");
