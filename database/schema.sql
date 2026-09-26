-- ==========================================
-- Odoo Hackathon Boilerplate Database Schema
-- Compatible with PostgreSQL & SQLite
-- ==========================================

-- 1. Create items table
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL DEFAULT 'General',
    is_active BOOLEAN DEFAULT TRUE,
    odoo_ref_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_items_title ON items(title);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);
CREATE INDEX IF NOT EXISTS idx_items_odoo_ref ON items(odoo_ref_id);

-- 2. Create hackathon teams table
CREATE TABLE IF NOT EXISTS hackathon_teams (
    id SERIAL PRIMARY KEY,
    team_name VARCHAR(150) NOT NULL UNIQUE,
    track VARCHAR(100) DEFAULT 'Main',
    project_title VARCHAR(255),
    odoo_partner_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create Odoo sync log audit table
CREATE TABLE IF NOT EXISTS odoo_sync_logs (
    id SERIAL PRIMARY KEY,
    sync_action VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    records_processed INTEGER DEFAULT 0,
    details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
