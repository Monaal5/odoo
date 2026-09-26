# StockSense – Execution Plan

> **Author**: @monaal  
> **Date**: Sep 26, 2026  
> **System**: Real-Time Inventory Management System (IMS)

---

## 📌 Overview & Objectives

StockSense replaces paper registers, spreadsheets, and ad-hoc tracking with a single, real-time **Inventory Management System (IMS)**. Every stock movement — receipt, delivery, transfer, adjustment — is validated and written to an **append-only Stock Ledger**, ensuring on-hand quantity per product per location is always current, derived, and fully auditable.

### Core Objectives
- **Live Operations Dashboard**: Give Inventory Managers a real-time, filterable view of stock health (KPIs, low-stock alerts, pending work).
- **Guided Staff Workflows**: Provide Warehouse Staff simple, step-by-step flows for picking, packing, transfers, and physical counts.
- **Auditable Stock Ledger**: Guarantee every quantity change is logged, reversible (via compensating entries), and traceable to a source document.
- **Native Multi-Warehouse Support**: Built-in support for multiple warehouses, locations, and nested racks from Day 1.

---

## 👥 Target Users & Roles

| Role | Primary Actions | Key Permissions |
| :--- | :--- | :--- |
| **Inventory Manager** | Create/edit products, review dashboard KPIs, validate receipts & deliveries, set reordering rules, manage warehouses | Full read/write; can void or override adjustments |
| **Warehouse Staff** | Pick, pack, transfer, count stock | Restricted to operations screens; cannot edit product master data or settings |

### Authentication & Role-Based Access Control (RBAC)
- **Flow**: Sign up / Log in, OTP-based password reset, redirect to Inventory Dashboard upon successful login.
- **Authorization**: Role field on the user profile dynamically drives navigation and action permissions.

---

## 🛠 Recommended Tech Stack

| Layer | Choice | Rationale |
| :--- | :--- | :--- |
| **Frontend** | React + TypeScript, Tailwind CSS | Fast dashboard & filter rendering, type safety, large component ecosystem |
| **Backend** | Node.js (NestJS) or Django / FastAPI | Clear module boundaries matching Products, Operations, and Settings |
| **Database** | PostgreSQL | Strong transactional integrity for stock ledger, relational fit for multi-location moves |
| **Auth** | JWT + OTP via Email/SMS (Twilio/SendGrid) | Secure authentication with password reset OTP requirement |
| **Realtime** | WebSockets or Polling | Live stock counts and KPI updates without full page reloads |
| **Hosting** | Docker containers on Cloud (AWS/GCP/Render) | Modular scaling per service |

> ⚠️ **Key Architectural Principle**: The **Stock Ledger** is an append-only table (`product_id`, `location_id`, `qty_delta`, `source_doc_type`, `source_doc_id`, `timestamp`, `user_id`). Stock levels are derived sums from the ledger and are **never edited directly**.

---

## 📅 Phased Implementation Roadmap

### Phase 1 — MVP Foundation (Weeks 1–3)
**Goal**: Usable single-warehouse system covering identity and product catalog.
- **Auth**: Sign up / Login, OTP password reset, session & role management.
- **Product Management**: CRUD for products (Name, SKU/Code, Category, Unit of Measure, Initial Stock).
- **Product Categories**: Category master management.
- **Single-Warehouse Stock Table**: Derived stock per product.
- **Core Shell Dashboard**: Left sidebar navigation (Products, Operations, Settings, Profile) & baseline KPIs.

### Phase 2 — Core Stock Operations (Weeks 4–6)
**Goal**: Inbound and outbound stock flows with full event logging.
- **Receipts (Incoming)**: Supplier, products, quantities (`Draft` → `Waiting` → `Ready` → `Done`). Validating auto-increases stock & appends to ledger.
- **Delivery Orders (Outgoing)**: Sales order / manual creation (`Pick` → `Pack` → `Validate`). Validating auto-decreases stock & appends to ledger.
- **Stock Ledger / Move History**: Filterable, read-only audit log by product, document type, status, and date.

### Phase 3 — Internal Transfers & Adjustments (Weeks 7–8)
**Goal**: Multi-location movements and physical count reconciliations.
- **Internal Transfers**: Move stock between warehouses/racks (`Main Warehouse` → `Production Floor`). Total stock unchanged; location updated.
- **Stock Adjustments**: Counted qty input vs recorded stock. System computes delta, writes ledger entry, and records reason/notes (damage, loss, count error).
- **Multi-Warehouse Support**: Nested location entity modeling (`Warehouse` → `Zone` → `Rack`).

### Phase 4 — Intelligence & Alerts (Weeks 9–10)
**Goal**: Transform dashboard into a real-time operations control center.
- **Dashboard KPIs**: Total products in stock, low-stock/out-of-stock count, pending receipts, pending deliveries, scheduled transfers.
- **Dynamic Filters**: By document type (`Receipt`, `Delivery`, `Transfer`, `Adjustment`), status, location, and category.
- **Low-Stock Alerts**: Reordering rules based on per-product min/max thresholds.
- **SKU Search**: Smart full-text search across catalog.

### Phase 5 — Scale & Polish (Weeks 11–13)
**Goal**: Production-ready, multi-warehouse setup with audit readiness.
- **Settings Module**: Warehouse management (Add/Edit/Deactivate), User & Role permissions.
- **Profile & Security**: Password/OTP settings, My Profile, Session logout.
- **Performance**: Pagination & indexing on stock ledger.
- **Reporting & Export**: CSV/PDF export of stock levels and move history.
- **Audit Hardening**: Immutable ledger log; who-did-what-when on every document.
- **Mobile/Tablet Views**: Minimalist staff views for picking, packing, and counting.
- **QA & Edge Cases**: Negative stock prevention, concurrent adjustment handling, document cancellation reversing via compensating entries.

### Phase 6 — AI-Powered Features (Weeks 14–16, Post-Launch)
**Goal**: Predictive and assisted operations using clean ledger history.
- **Demand Forecasting & Smart Reorder**: Predict future consumption based on historical ledger velocity; auto-suggest receipts before hitting min threshold.
- **Anomaly Detection**: Flag unusual shrinkage, abnormal delivery sizes, or repeated damage adjustments.
- **Natural Language Assistant**: Staff query support ("How much steel is in Rack B?", "What is low this week?").
- **Smart Putaway / Slotting**: Recommend optimal rack locations based on turnover frequency.
- **OCR Invoice Auto-Fill**: Scan packing slip / supplier invoice to pre-fill receipt lines.

---

## 🗄 Core Data Model Schemas

- **User**: `id`, `name`, `email`, `password_hash`, `role` (`Inventory Manager` | `Warehouse Staff`).
- **Product**: `id`, `name`, `sku`, `category_id`, `unit_of_measure`, `reorder_min`, `reorder_max`.
- **Location**: `id`, `name`, `parent_location_id` (supports nested Warehouse → Zone → Rack).
- **StockLevel**: `product_id`, `location_id`, `quantity` (derived/cached from ledger).
- **Receipt**: `id`, `supplier`, `lines`, `status` (`Draft` | `Waiting` | `Ready` | `Done`).
- **DeliveryOrder**: `id`, `customer_ref`, `lines`, `status`.
- **InternalTransfer**: `id`, `product_id`, `from_location_id`, `to_location_id`, `qty`, `status`.
- **Adjustment**: `id`, `product_id`, `location_id`, `counted_qty`, `delta`, `reason`.
- **StockLedgerEntry**: `id`, `product_id`, `location_id`, `qty_delta`, `source_doc_type`, `source_doc_id`, `timestamp`, `user_id`.

---

## 🛡 Risk Management Matrix

| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Stock Drift between StockLevel & Ledger** | High | Treat `StockLedgerEntry` as the sole source of truth; `StockLevel` is purely derived/cached. |
| **Race Conditions in Concurrent Adjustments** | High | Use DB-level row-level locking (`SELECT ... FOR UPDATE`) or optimistic concurrency. |
| **Scope Creep before core stability** | Medium | Strictly freeze Phases 1–3 before introducing analytics or mobile optimization. |
| **Complex UI confusing warehouse staff** | Medium | Provide streamlined, simplified operational views for staff vs managerial dashboards. |
| **Cancelled Documents Corrupting History** | High | Never delete ledger records; document cancellations issue compensating inverse ledger entries. |
