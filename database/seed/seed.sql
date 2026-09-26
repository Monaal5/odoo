-- ==========================================
-- Hackathon Seed Data
-- ==========================================

INSERT INTO items (title, description, category, is_active, odoo_ref_id) VALUES
('Odoo ERP Connector', 'XML-RPC wrapper for syncing contacts and sales orders', 'Integration', TRUE, 1001),
('AI Inventory Predictor', 'Machine learning model predicting warehouse stock requirements', 'AI / ML', TRUE, 1002),
('POS Cashier Widget', 'Custom Odoo Owl framework widget for point of sale', 'Frontend', TRUE, 1003),
('Automated Invoice Parser', 'OCR tool parsing PDF receipts directly into Odoo Accounting', 'Automation', TRUE, 1004)
ON CONFLICT DO NOTHING;

INSERT INTO hackathon_teams (team_name, track, project_title, odoo_partner_id) VALUES
('Team Innovators', 'ERP Enhancement', 'Smart Odoo Inventory Assistant', 501),
('ByteCrafters', 'AI & Automation', 'Odoo PDF Auto-Accountant', 502)
ON CONFLICT DO NOTHING;

INSERT INTO odoo_sync_logs (sync_action, status, records_processed, details) VALUES
('INITIAL_SEED', 'SUCCESS', 4, 'Seeded default hackathon demo items');
