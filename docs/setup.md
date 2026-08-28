# Setup & Deployment Guide - CanteenOS

This guide covers local development setup and cloud deployment to **Vercel** (Serverless Python Functions + Static Frontend) with **Neon PostgreSQL** (Serverless Database).

---

## 1. Local Development Quickstart

### A. Clone & Virtual Environment
```bash
# 1. Clone or navigate to the project directory
cd "mini project"

# 2. Create Python virtual environment (Python 3.10, 3.11, or 3.12 recommended)
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
For zero-configuration local development, the app defaults to SQLite (`sqlite:///./canteen.db`) if `DATABASE_URL` is omitted. If you have a local PostgreSQL instance running:
```ini
DATABASE_URL=postgresql://postgres:yourpassword@127.0.0.1:5432/canteen_db
```

### C. Start the Backend API
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
On startup, FastAPI automatically verifies the database schema and seeds the catalog data (roles, counters, categories, 25 South Indian dishes, initial inventory stock, and default admin/staff accounts).

### D. Open the Application
- Open **`http://localhost:8000`** directly in your browser (FastAPI serves both the API endpoints and the static frontend).
- Or run a static server in a separate terminal:
  ```bash
  python3 -m http.server 3000 --directory frontend
  ```
  and visit `http://localhost:3000`. The frontend automatically connects to the backend at `http://127.0.0.1:8000`.

---

## 2. Neon Managed PostgreSQL Setup

Vercel Python functions run in ephemeral serverless environments, requiring an external managed database. **Neon** (`https://neon.tech`) provides a free-tier serverless PostgreSQL instance with built-in connection pooling.

### Steps to Provision Neon Database:
1. Sign up at [neon.tech](https://neon.tech) (free tier).
2. Create a new project (e.g. `canteen-os`).
3. In the Neon Dashboard, go to **Connection Details**:
   - Ensure the **"Pooled connection"** checkbox is **checked** (`-pooler` in the hostname).
   - Copy the connection string. It will look like:
     ```text
     postgresql://username:password@ep-sample-pooler.region.aws.neon.tech/canteen_db?sslmode=require
     ```
4. **Why Pooled?** In serverless architectures (like Vercel Functions), thousands of function invocations can spawn simultaneously. Neon's connection pooler (PgBouncer) multiplexes these connections to prevent database connection exhaustion.
5. Set this connection string as the `DATABASE_URL` environment variable on Vercel and in your production `.env`.

---

## 3. Vercel Cloud Deployment (Unified Architecture)

The repository is configured for **Single-Project Unified Deployment** on Vercel:
- `/api/*` routes are handled by the serverless Python function at `api/index.py` (FastAPI).
- All static pages (`/`, `/menu`, `/orders`, `/cart`, `/wallet`, `/admin/*`) are served directly by Vercel's Edge CDN via `vercel.json` rewrites.

### Deployment Steps:
1. Push your repository to **GitHub** (ensure `.env` is ignored by `.gitignore`).
2. Go to [vercel.com](https://vercel.com) and click **"Add New Project"**.
3. Import your GitHub repository.
4. In **Project Settings $\rightarrow$ Environment Variables**, add the following:

| Variable Name | Recommended Value / Format | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://user:pass@ep-pooler.region.aws.neon.tech/dbname?sslmode=require` | Neon Pooled PostgreSQL connection string |
| `SECRET_KEY` | *(Generate via `openssl rand -hex 32`)* | Cryptographic JWT signing secret |
| `ALLOWED_ORIGINS` | `https://your-canteen-app.vercel.app` *(update after first deploy)* | Permitted CORS origins |
| `ENV` | `production` | Environment mode |
| `DEBUG` | `false` | Disable debug stack traces in production |
| `UPI_VPA` | `canteen@upi` | Canteen UPI ID for payment QR generation |
| `UPI_PAYEE_NAME` | `Campus Canteen Services` | Canteen Payee Name |

5. Click **Deploy**. Vercel will build the Python serverless function and static assets.
6. Verify deployment by visiting:
   - `https://your-app.vercel.app/api/health` $\rightarrow$ Returns `{"status": "healthy", ...}`
   - `https://your-app.vercel.app/` $\rightarrow$ Loads CanteenOS home page

---

## 4. Real-Time Architecture Note

Vercel's Serverless Python runtime does **not** support persistent background daemon processes or WebSockets. 

CanteenOS is purposefully designed with **Stateless HTTP Polling**:
- **Live Token Tracker (`token.html`):** Polls `/api/tokens/active/me` or `/api/tokens/{id}` every 3.5 seconds.
- **Kiosk TV (`kiosk.html`):** Polls `/api/tokens/kiosk/live` every 4.0 seconds.
- **Queue View (`queue.html`):** Polls `/api/tokens/live-board` every 5.0 seconds.
- **Notifications (`notifications.js`):** Polls `/api/notifications/unread-count` periodically.

This architecture requires **zero WebSocket infrastructure** and executes seamlessly on standard Vercel serverless functions.

---

## 5. Running Automated Tests

Run the complete test suite:
```bash
./venv/bin/pytest -v
```

---

## 6. Seed Accounts & Master Data

On first startup against a clean database, CanteenOS seeds:
- **Roles:** Admin (1), Staff (2), Student (3)
- **Counters:** Counter 1 (Tiffins/Meals), Counter 2 (Desserts/Sweets), Counter 3 (Beverages/Cafe)
- **Menu Catalog:** 25 authentic South Indian dishes with prices, calories, protein, carbs, fats, prep times, and image paths.
- **Operational Accounts:**
  - **Administrator:** `admin@canteen.edu` / `Admin@123`
  - **Counter Staff:** `staff@canteen.edu` / `Staff@123`
