-- ============================================================================
-- StockSense Inventory Management System (IMS) - Database Schema
-- Compatible with PostgreSQL & SQLite
-- ============================================================================

-- 1. Item/Product Master Table
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
    supplier VARCHAR(255),
    supplier_name VARCHAR(255),
    warehouse_id VARCHAR(100),
    location_id INTEGER DEFAULT 1,
    status VARCHAR(50) NOT NULL DEFAULT 'Draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS receipt_items (
    id SERIAL PRIMARY KEY,
    receipt_id INTEGER NOT NULL REFERENCES receipts(id) ON DELETE CASCADE,
    product_id VARCHAR(100) NOT NULL,
    location_id INTEGER DEFAULT 1,
    quantity NUMERIC NOT NULL
);

-- 3. Outgoing Delivery Orders Document Table
CREATE TABLE IF NOT EXISTS deliveries (
    id SERIAL PRIMARY KEY,
    delivery_number VARCHAR(100) NOT NULL UNIQUE,
    customer VARCHAR(255),
    customer_name VARCHAR(255),
    warehouse_id VARCHAR(100),
    location_id INTEGER DEFAULT 1,
    status VARCHAR(50) NOT NULL DEFAULT 'Draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS delivery_items (
    id SERIAL PRIMARY KEY,
    delivery_id INTEGER NOT NULL REFERENCES deliveries(id) ON DELETE CASCADE,
    product_id VARCHAR(100) NOT NULL,
    location_id INTEGER DEFAULT 1,
    quantity NUMERIC NOT NULL
);

-- 4. Internal Transfers Table
CREATE TABLE IF NOT EXISTS transfers (
    id SERIAL PRIMARY KEY,
    transfer_number VARCHAR(100) NOT NULL UNIQUE,
    product_id VARCHAR(100) NOT NULL,
    from_location_id INTEGER DEFAULT 1,
    to_location_id INTEGER DEFAULT 1,
    from_warehouse_id VARCHAR(100),
    to_warehouse_id VARCHAR(100),
    quantity NUMERIC NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Stock Adjustments Table
CREATE TABLE IF NOT EXISTS adjustments (
    id SERIAL PRIMARY KEY,
    adjustment_number VARCHAR(100) NOT NULL UNIQUE,
    product_id VARCHAR(100) NOT NULL,
    location_id INTEGER DEFAULT 1,
    warehouse_id VARCHAR(100),
    counted_qty NUMERIC NOT NULL,
    system_qty NUMERIC NOT NULL,
    delta_qty NUMERIC NOT NULL,
    reason VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Derived Stock Levels Cache Table
CREATE TABLE IF NOT EXISTS stock_levels (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100) NOT NULL,
    location_id INTEGER DEFAULT 1,
    warehouse_id VARCHAR(100),
    quantity NUMERIC NOT NULL DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Append-Only Stock Ledger Audit Table
CREATE TABLE IF NOT EXISTS stock_ledger (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100) NOT NULL,
    location_id INTEGER DEFAULT 1,
    warehouse_id VARCHAR(100),
    qty_delta NUMERIC NOT NULL,
    source_doc_type VARCHAR(50),
    source_doc_id VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ledger_product ON stock_ledger(product_id);
CREATE INDEX IF NOT EXISTS idx_ledger_location ON stock_ledger(location_id);
CREATE INDEX IF NOT EXISTS idx_ledger_doc_type ON stock_ledger(source_doc_type);

-- 7b. Secondary Stock Ledger Entries Table for API compatibility
CREATE TABLE IF NOT EXISTS stock_ledger_entries (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100) NOT NULL,
    warehouse_id VARCHAR(100),
    location_id INTEGER DEFAULT 1,
    qty_delta NUMERIC NOT NULL,
    source_document_type VARCHAR(50),
    source_document_id VARCHAR(100),
    source_doc_type VARCHAR(50),
    source_doc_id VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. Reorder Rules Table (Min/Max Thresholds)
CREATE TABLE IF NOT EXISTS reorder_rules (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100) NOT NULL,
    location_id INTEGER DEFAULT 1,
    warehouse_id VARCHAR(100),
    min_qty NUMERIC NOT NULL DEFAULT 5,
    max_qty NUMERIC NOT NULL DEFAULT 50,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 9. Generated Low-Stock Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(100) NOT NULL,
    location_id INTEGER DEFAULT 1,
    warehouse_id VARCHAR(100),
    current_stock NUMERIC NOT NULL,
    min_stock NUMERIC NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    message VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerts_product ON alerts(product_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);

-- 10. Users Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'inventory_staff',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 11. Products Table
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    unit_of_measure VARCHAR(50) DEFAULT 'Units',
    category_id VARCHAR(100),
    reorder_min NUMERIC DEFAULT 0,
    reorder_max NUMERIC DEFAULT 0,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 12. Warehouses Table
CREATE TABLE IF NOT EXISTS warehouses (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    address TEXT,
    parent_id VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 13. Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 14. Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    entity VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON audit_logs(entity);
