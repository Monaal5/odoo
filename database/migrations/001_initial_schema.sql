-- Migration: 001_initial_schema.sql
-- Description: Create initial tables for hackathon items, teams, and odoo logs

BEGIN;

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

CREATE TABLE IF NOT EXISTS hackathon_teams (
    id SERIAL PRIMARY KEY,
    team_name VARCHAR(150) NOT NULL UNIQUE,
    track VARCHAR(100) DEFAULT 'Main',
    project_title VARCHAR(255),
    odoo_partner_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS odoo_sync_logs (
    id SERIAL PRIMARY KEY,
    sync_action VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    records_processed INTEGER DEFAULT 0,
    details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMIT;
