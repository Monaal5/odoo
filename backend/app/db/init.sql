-- ============================================================
-- StockSense IMS — Database Initialisation Script
-- Run once against your PostgreSQL database:
--   psql -U postgres -d stocksense -f init.sql
-- ============================================================

-- ---------------------
-- EXTENSIONS
-- ---------------------
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- gen_random_uuid()

-- ---------------------
-- USERS
-- ---------------------
CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          VARCHAR(255)        NOT NULL,
    email         VARCHAR(255)        NOT NULL UNIQUE,
    password_hash TEXT                NOT NULL,
    role          VARCHAR(50)         NOT NULL DEFAULT 'warehouse_staff'
                      CHECK (role IN ('inventory_manager', 'warehouse_staff')),
    is_active     BOOLEAN             NOT NULL DEFAULT TRUE,
    otp_code      VARCHAR(6),
    otp_expires_at TIMESTAMPTZ,
    created_at    TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ---------------------
-- CATEGORIES
-- ---------------------
CREATE TABLE IF NOT EXISTS categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- ---------------------
-- WAREHOUSES / LOCATIONS
-- ---------------------
CREATE TABLE IF NOT EXISTS warehouses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    code            VARCHAR(50)  NOT NULL UNIQUE,   -- short reference, e.g. WH01
    address         TEXT,
    parent_id       UUID REFERENCES warehouses(id) ON DELETE SET NULL,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_warehouses_parent ON warehouses(parent_id);

-- ---------------------
-- PRODUCTS
-- ---------------------
CREATE TABLE IF NOT EXISTS products (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    sku             VARCHAR(100) NOT NULL UNIQUE,
    category_id     UUID REFERENCES categories(id) ON DELETE SET NULL,
    unit_of_measure VARCHAR(50)  NOT NULL DEFAULT 'units',
    reorder_min     NUMERIC(12,3) NOT NULL DEFAULT 0,
    reorder_max     NUMERIC(12,3) NOT NULL DEFAULT 0,
    description     TEXT,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_sku      ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);

-- ---------------------
-- RECEIPTS & RECEIPT ITEMS
-- ---------------------
CREATE TABLE IF NOT EXISTS receipts (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_number VARCHAR(50) NOT NULL UNIQUE,
    supplier       VARCHAR(255) NOT NULL,
    warehouse_id   UUID REFERENCES warehouses(id) ON DELETE SET NULL,
    status         VARCHAR(50) NOT NULL DEFAULT 'Draft' CHECK (status IN ('Draft', 'Waiting', 'Ready', 'Done', 'Canceled')),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS receipt_items (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    receipt_id UUID NOT NULL REFERENCES receipts(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    quantity   NUMERIC(12,3) NOT NULL CHECK (quantity > 0)
);

-- ---------------------
-- DELIVERIES & DELIVERY ITEMS
-- ---------------------
CREATE TABLE IF NOT EXISTS deliveries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_number VARCHAR(50) NOT NULL UNIQUE,
    customer        VARCHAR(255) NOT NULL,
    warehouse_id    UUID REFERENCES warehouses(id) ON DELETE SET NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'Draft' CHECK (status IN ('Draft', 'Waiting', 'Ready', 'Done', 'Canceled')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS delivery_items (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_id UUID NOT NULL REFERENCES deliveries(id) ON DELETE CASCADE,
    product_id  UUID NOT NULL REFERENCES products(id),
    quantity    NUMERIC(12,3) NOT NULL CHECK (quantity > 0)
);

-- ---------------------
-- STOCK LEDGER (Append-Only Source of Truth)
-- ---------------------
CREATE TABLE IF NOT EXISTS stock_ledger_entries (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id           UUID NOT NULL REFERENCES products(id),
    warehouse_id         UUID REFERENCES warehouses(id),
    qty_delta            NUMERIC(12,3) NOT NULL,
    source_document_type VARCHAR(50) NOT NULL,
    source_document_id   UUID NOT NULL,
    timestamp            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id              UUID REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_stock_ledger_product   ON stock_ledger_entries(product_id);
CREATE INDEX IF NOT EXISTS idx_stock_ledger_warehouse ON stock_ledger_entries(warehouse_id);

-- ---------------------
-- STOCK LEVELS (Derived / Cached)
-- ---------------------
CREATE TABLE IF NOT EXISTS stock_levels (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id   UUID NOT NULL REFERENCES products(id),
    warehouse_id UUID REFERENCES warehouses(id),
    quantity     NUMERIC(12,3) NOT NULL DEFAULT 0,
    CONSTRAINT unq_product_warehouse UNIQUE (product_id, warehouse_id)
);

