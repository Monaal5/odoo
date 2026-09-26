-- ==========================================
-- StockSense Inventory Seed Data
-- ==========================================

INSERT INTO items (title, description, category, is_active) VALUES
('Fresh Fuji Apples', 'Crisp Grade A Fuji Apples (1kg bags)', 'Produce', TRUE),
('Industrial Steel Rods 20mm', 'Heavy-duty construction steel rods (2m)', 'Raw Materials', TRUE),
('Smart Barcode Terminal', 'Handheld wireless scanner for warehouse staff', 'Hardware', TRUE)
ON CONFLICT DO NOTHING;
