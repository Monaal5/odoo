# 🚀 Odoo Hackathon Boilerplate

> A plug-and-play, full-stack boilerplate built for **Odoo Hackathons**, featuring a modern interactive frontend, a high-performance **FastAPI** backend, database management, and out-of-the-box **Odoo XML-RPC ERP integration**.

---

## 📁 Repository Structure

```text
Odoo_Hackathon_Boilerplate/
│
├── frontend/
│   ├── index.html          # Interactive Web UI & API Tester Dashboard
│   ├── css/
│   │   └── style.css       # Futuristic Dark/Glassmorphic Styling System
│   ├── js/
│   │   └── app.js          # Dynamic DOM logic, API console & Odoo sync
│   └── assets/
│       └── images/         # Static visual assets & diagrams
│
├── backend/
│   ├── requirements.txt    # Python dependencies (FastAPI, SQLAlchemy, Uvicorn)
│   ├── app/
│   │   ├── main.py         # FastAPI App Entrypoint & CORS configuration
│   │   ├── api/            # API Route definitions & health checks
│   │   ├── models/         # SQLAlchemy ORM models (Items, Odoo Refs)
│   │   ├── schemas/        # Pydantic data schemas
│   │   ├── services/       # Business logic & Odoo XML-RPC connectors
│   │   ├── db/
│   │   │   └── database.py # Database session & engine setup
│   │   └── core/
│   │       └── config.py   # Environment Settings (BaseSettings)
│   └── tests/
│       └── test_main.py    # Pytest API test suite
│
├── database/
│   ├── schema.sql          # Table definitions & DDL scripts
│   ├── migrations/         # Database migration scripts
│   └── seed/
│       └── seed.sql        # Hackathon demo seed data
│
├── docs/
│   └── API.md              # Comprehensive Endpoint & Odoo Integration Specs
│
├── .env.example            # Environment variables template
├── .gitignore              # Standard git ignore rules
└── README.md               # Project documentation
```

---

## ⚡ Quick Start Guide

### 1. Backend Setup

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

# Copy environment variables
cp ../.env.example .env

# Run FastAPI development server
uvicorn app.main:app --reload --port 8000
```

Once started, access:
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/api/v1/health`

---

### 2. Frontend Setup

Simply open `frontend/index.html` in your browser, or serve it using any standard HTTP server:

```bash
# Using Python built-in HTTP server
cd frontend
python -m http.server 3000
```

Then visit `http://localhost:3000`.

---

### 3. Database Setup

By default, the application uses **SQLite** (`hackathon.db`) requiring **zero database installation**. 

To use **PostgreSQL** or **Odoo PostgreSQL Database**:
1. Update `DATABASE_URL` in your `.env` file:
   ```env
   DATABASE_URL="postgresql://username:password@localhost:5432/odoo_hackathon"
   ```
2. Execute initial schema & seed data:
   ```bash
   psql -U username -d odoo_hackathon -f database/schema.sql
   psql -U username -d odoo_hackathon -f database/seed/seed.sql
   ```

---

## 🔗 Odoo XML-RPC Integration

Configure your Odoo connection parameters in `.env`:

```env
ODOO_URL="http://localhost:8069"
ODOO_DB="odoo_db"
ODOO_USER="admin"
ODOO_PASSWORD="admin"
```

The backend includes built-in services (`OdooService`) to authenticate and query any Odoo ORM model (`res.partner`, `product.template`, `sale.order`, `account.move`) via XML-RPC.

---

## 🧪 Running Unit Tests

```bash
cd backend
pytest -v
```

---

## 💡 Hackathon Tips

1. **Fast Prototyping**: SQLite is enabled by default so you can build features immediately without database dependencies.
2. **CORS Enabled**: Backend permits all origins during development (`allow_origins=["*"]`) for easy frontend prototyping.
3. **Interactive Console**: Use the included frontend dashboard (`frontend/index.html`) to test live API calls and Odoo connectivity in real-time.
