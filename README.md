# 📦 StockSense – Real-Time Inventory Management System (IMS)

> StockSense replaces spreadsheets and ad-hoc stock tracking with a real-time **Inventory Management System (IMS)**. Every stock movement — receipt, delivery, internal transfer, stock adjustment — is validated and recorded in an **append-only Stock Ledger**, ensuring current on-hand stock per product per location is accurate, derived, and 100% auditable.

---

## 📁 Repository Structure

```text
odoo/
├── frontend/
│   ├── index.html          # StockSense Developer Suite & Control Center
│   ├── css/
│   │   └── style.css       # Modern Glassmorphic Dark Design System
│   └── js/
│       └── app.js          # Tab switching, health monitor & API triggers
│
├── backend/
│   ├── requirements.txt    # FastAPI, Uvicorn, SQLAlchemy, psycopg2-binary, pytest
│   ├── app/
│   │   ├── main.py         # FastAPI application entry point with CORS
│   │   ├── api/
│   │   │   ├── endpoints.py# System health & Item CRUD routes
│   │   │   ├── receipts.py # Receipts endpoints (Create, Validate, List)
│   │   │   ├── deliveries.py# Deliveries endpoints (Create, Validate, List)
│   │   │   ├── transfers.py# Internal Transfers endpoints (Create, Validate)
│   │   │   ├── adjustments.py# Stock Adjustments count reconciliation
│   │   │   ├── ledger.py   # Append-only Stock Ledger audit history
│   │   │   └── dashboard.py# Real-time operational dashboard KPIs
│   │   ├── models/
│   │   │   ├── item.py     # Product Catalog Item model
│   │   │   ├── receipt.py  # Receipt & ReceiptItem models
│   │   │   ├── delivery.py # Delivery & DeliveryItem models
│   │   │   ├── transfer.py # InternalTransfer model
│   │   │   ├── adjustment.py# StockAdjustment model
│   │   │   ├── stock_level.py# Derived StockLevel cache model
│   │   │   └── stock_ledger.py# Append-only StockLedgerEntry model
│   │   ├── schemas/        # Pydantic V2 Request & Response schemas
│   │   ├── services/
│   │   │   ├── inventory_service.py # Core Receipts, Deliveries, Transfers logic
│   │   │   ├── ledger_service.py    # Atomic stock ledger recording & level sync
│   │   │   └── dashboard_service.py # Operational KPIs calculation
│   │   ├── db/
│   │   │   └── database.py # PostgreSQL connection engine with SQLite fallback
│   │   └── core/
│   │       └── config.py   # Pydantic BaseSettings environment configuration
│   └── tests/
│       ├── test_main.py    # Core system tests
│       └── test_inventory_operations.py # Complete operations E2E test suite
│
├── database/
│   ├── schema.sql          # Clean DDL scripts (PostgreSQL/SQLite)
│   ├── migrations/
│   │   └── 001_initial_schema.sql # Versioned migration script
│   └── seed/
│       └── seed.sql        # StockSense seed dataset
│
├── docs/
│   └── StockSense_Execution_Plan.md # Project Architecture & Roadmap
│
├── view_database.py        # Terminal database viewer CLI utility
├── StockSense_Execution_Plan.md # System specification
├── .env.example            # Environment variables template
├── .gitignore              # Standard git ignore rules
└── README.md               # Project documentation
```

---

## ⚡ Quick Start Guide

### 1. Backend Server Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once started, access:
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/api/v1/health`
- **Dashboard KPIs**: `http://localhost:8000/api/v1/dashboard/kpis`

---

### 2. Frontend Setup

Open `frontend/index.html` directly in your browser or run via Python HTTP server:

```bash
cd frontend
python -m http.server 3000
```
Visit `http://localhost:3000`.

---

### 3. Database Inspection & Utility

To view all database tables (`items`, `stock_ledger`, `stock_levels`, `receipts`, `deliveries`, `transfers`, `adjustments`) directly in your terminal:

```bash
python view_database.py
```

---

## 🧪 Unit Tests Suite

```bash
cd backend
python -m pytest tests/
```
All unit test suites pass 100%.
