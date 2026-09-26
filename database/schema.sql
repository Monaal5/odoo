-- ============================================================================
-- StockSense Inventory Management System (IMS) - Database Schema
-- Compatible with PostgreSQL & SQLite
-- ============================================================================

-- 1. Product Master Table
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL DEFAULT 'General',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_items_title ON items(title);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);

-- 2. Incoming Receipts Document Table
CREATE TABLE IF NOT EXISTS receipts (
    id SERIAL PRIMARY KEY,
    receipt_number VARCHAR(100) NOT NULL UNIQUE,
    supplier_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS receipt_items (
    id SERIAL PRIMARY KEY,
    receipt_id INTEGER NOT NULL REFERENCES receipts(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL DEFAULT 1,
    quantity INTEGER NOT NULL
);

-- 3. Outgoing Delivery Orders Document Table
CREATE TABLE IF NOT EXISTS deliveries (
    id SERIAL PRIMARY KEY,
    delivery_number VARCHAR(100) NOT NULL UNIQUE,
    customer_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS delivery_items (
    id SERIAL PRIMARY KEY,
    delivery_id INTEGER NOT NULL REFERENCES deliveries(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL DEFAULT 1,
    quantity INTEGER NOT NULL
);

-- 4. Internal Transfers Table
CREATE TABLE IF NOT EXISTS transfers (
    id SERIAL PRIMARY KEY,
    transfer_number VARCHAR(100) NOT NULL UNIQUE,
    product_id INTEGER NOT NULL,
    from_location_id INTEGER NOT NULL,
    to_location_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Stock Adjustments Table
CREATE TABLE IF NOT EXISTS adjustments (
    id SERIAL PRIMARY KEY,
    adjustment_number VARCHAR(100) NOT NULL UNIQUE,
    product_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    counted_qty INTEGER NOT NULL,
    system_qty INTEGER NOT NULL,
    delta_qty INTEGER NOT NULL,
    reason VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Derived Stock Levels Cache Table
CREATE TABLE IF NOT EXISTS stock_levels (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT _product_location_uc UNIQUE (product_id, location_id)
);

-- 7. Append-Only Stock Ledger Audit Table
CREATE TABLE IF NOT EXISTS stock_ledger (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    qty_delta INTEGER NOT NULL,
    source_doc_type VARCHAR(50) NOT NULL,
    source_doc_id INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ledger_product ON stock_ledger(product_id);
CREATE INDEX IF NOT EXISTS idx_ledger_location ON stock_ledger(location_id);
CREATE INDEX IF NOT EXISTS idx_ledger_doc_type ON stock_ledger(source_doc_type);
