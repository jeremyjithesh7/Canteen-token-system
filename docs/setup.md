# Setup & Deployment Guide - Digital Canteen Token System

## 1. Prerequisites
- **Python 3.10+** (tested on 3.11/3.12/3.13)
- **PostgreSQL 14+** (or SQLite fallback for zero-configuration testing)
- **Modern Web Browser** (Chrome, Firefox, Safari, Edge)

---

## 2. Fast Setup (Local Development)

### A. Clone & Virtual Environment Setup
```bash
# 1. Navigate to project root
cd "Digital Canteen Token System"

# 2. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### B. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default `.env` configuration:
```ini
DATABASE_URL=sqlite:///./canteen.db
SECRET_KEY=canteen-super-secret-key-change-in-production-2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```
*(For production PostgreSQL, set `DATABASE_URL=postgresql://user:password@localhost:5432/canteen_db`)*

### C. Start Backend API & Automatic Database Seeder
```bash
source venv/bin/activate
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
*The backend automatically creates all 20 database tables and seeds demo counters, accounts, food items, and historical analytics.*

### D. Start Frontend Client Server
In a second terminal window:
```bash
python3 -m http.server 3000 --directory frontend
```
Open **`http://localhost:3000`** in your browser.

---

## 3. Running Automated Tests

Run the complete 32-test automated test suite:
```bash
./venv/bin/pytest -v tests/
```

---

## 4. Default Demo Accounts

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Student** | `student@canteen.edu` | `Student@123` | Order food, track live QR token, view loyalty tier |
| **Kitchen Staff** | `staff@canteen.edu` | `Staff@123` | Advance tokens in Kanban lanes, view kitchen queue |
| **Administrator** | `admin@canteen.edu` | `Admin@123` | Full portal: revenue charts, demand overrides, CSV export |
