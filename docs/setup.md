# Setup & Deployment Guide - CanteenOS

This guide covers local development setup and cloud deployment using the clean split architecture: **Render** (Persistent FastAPI Web Service) + **Vercel** (Static Frontend CDN) + **Neon PostgreSQL** (Managed Database).

---

## 1. Local Development Quickstart

### A. Clone & Virtual Environment
```bash
# 1. Navigate to the project directory
cd "mini project"

# 2. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### B. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
For zero-configuration local development, the app defaults to SQLite (`sqlite:///./canteen.db`) if `DATABASE_URL` is omitted. If you have a local PostgreSQL instance or Neon connection string:
```ini
DATABASE_URL=postgresql://postgres:yourpassword@127.0.0.1:5432/canteen_db
```

### C. Start the Backend API
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
On startup, FastAPI automatically verifies the database schema and seeds the catalog data (roles, counters, categories, 25 South Indian dishes, initial inventory stock, and default admin/staff accounts).

### D. Open the Application
- Open **`http://localhost:8000`** directly in your browser (FastAPI static mount serves the frontend).
- Or run a static server in a separate terminal:
  ```bash
  python3 -m http.server 3000 --directory frontend
  ```
  and visit `http://localhost:3000`. The frontend automatically connects to the backend at `http://127.0.0.1:8000`.

---

## 2. Production Architecture Overview

- **Backend:** Hosted on **Render** as a persistent web service running `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`.
- **Frontend:** Hosted on **Vercel** with Root Directory set to `frontend/`.
- **Database:** Hosted on **Neon** using the pooled connection string (`-pooler`).

For complete production deployment instructions, see [docs/deployment.md](file:///Users/jeremyjithesh/mini%20project/docs/deployment.md).

---

## 3. Running Automated Tests

Run the complete test suite:
```bash
source venv/bin/activate && pytest -v
```

---

## 4. Default Accounts & Master Data

On first startup against a clean database, CanteenOS seeds:
- **Roles:** Admin (1), Staff (2), Student (3)
- **Counters:** Counter 1 (Tiffins/Meals), Counter 2 (Desserts/Sweets), Counter 3 (Beverages/Cafe)
- **Menu Catalog:** 25 authentic South Indian dishes with nutrition data, prep times, and image paths.
- **Operational Accounts:**
  - **Administrator:** `admin@canteen.edu` / `Admin@123`
  - **Counter Staff:** `staff@canteen.edu` / `Staff@123`
