# 🚀 Production Deployment Guide - CanteenOS (Vercel & Neon PostgreSQL)

This document is the verified, production deployment manual for **CanteenOS**. It details the exact architecture, environment variables, and verification steps required to deploy the system to **Vercel** and **Neon PostgreSQL**.

---

## 1. Target Architecture Overview

CanteenOS utilizes a **Unified Serverless Monorepo** on Vercel:

- **Frontend (`frontend/`):** Pure vanilla HTML5, CSS3, and modern JavaScript (ES6+). Served globally with zero build step via Vercel's High-Performance Edge CDN.
- **Backend API (`api/index.py` $\rightarrow$ `backend/`):** FastAPI ASGI application executed as ephemeral Python Serverless Functions.
- **Database:** Serverless PostgreSQL via **Neon** using **PgBouncer connection pooling**.
- **Real-Time Layer:** Stateless HTTP polling (`setInterval` at 3.5s–5.0s) for live token tracking and kiosk displays — completely eliminating WebSocket dependencies to adhere to Vercel's serverless runtime constraints.

---

## 2. Step 1: Database Setup (Neon PostgreSQL)

1. Sign up or log in at **[neon.tech](https://neon.tech)** (Free Tier supported).
2. Click **Create Project** (e.g. `canteen-os-prod`).
3. In the Neon Dashboard under **Connection Details**:
   - Check the **"Pooled connection"** checkbox (`-pooler` in the host domain).
   - Copy the generated connection string.
4. **Format Verification:**
   ```text
   postgresql://[user]:[password]@ep-[name]-pooler.[region].aws.neon.tech/[dbname]?sslmode=require
   ```
   > [!IMPORTANT]
   > **Why Pooled?** Ephemeral serverless functions scale up concurrently. Without a connection pooler, high student traffic would quickly exceed PostgreSQL's max connection threshold. Neon's PgBouncer pooler maintains connection stability under peak lunch rush.

---

## 3. Step 2: Vercel Cloud Deployment

### A. Push Code to GitHub
Ensure your latest changes are pushed to your GitHub repository:
```bash
git push origin main
```

### B. Import to Vercel
1. Log in to **[vercel.com](https://vercel.com)** and click **"Add New Project"**.
2. Select your `Canteen-token-system` repository.
3. Keep the default root directory (`./`).
4. **Framework Preset:** Leave as `Other` (Vercel auto-detects `vercel.json` and Python functions via `api/index.py`).

### C. Configure Environment Variables
In the **Environment Variables** section, add the following 5 variables:

| Variable Name | Exact Format / Example Value | Purpose |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://user:pass@ep-...-pooler.../dbname?sslmode=require` | Pooled Neon PostgreSQL connection string |
| `SECRET_KEY` | *(Run `openssl rand -hex 32`)* | Cryptographic JWT signing secret (min 32 bytes) |
| `ALLOWED_ORIGINS` | `https://your-canteen-app.vercel.app,http://localhost:3000` | Allowed CORS origins (comma-separated) |
| `ENV` | `production` | Declares production environment |
| `DEBUG` | `false` | Disables debug stack traces & masks server errors |

*(Optional Campus UPI Settings: `UPI_VPA="canteen@upi"`, `UPI_PAYEE_NAME="Campus Canteen"`, `CAMPUS_GST_PERCENT="5.0"`)*

### D. Click Deploy
Vercel will install dependencies from `requirements.txt`, package the serverless function, configure rewrites, and deploy the application.

---

## 4. Step 3: Post-Deployment Verification

### 1. Check API Health & Database Connection
Visit: `https://your-canteen-app.vercel.app/api/health`

**Expected JSON Response:**
```json
{
  "status": "healthy",
  "service": "Digital Canteen Token System",
  "environment": "production",
  "debug": false,
  "database": "connected"
}
```
- If `"database": "connected"`, the database tables were automatically verified and master data seeded.

### 2. Verify Initial Master Accounts
Sign in at `https://your-canteen-app.vercel.app/login.html`:
- **Admin Portal:** `admin@canteen.edu` / `Admin@123`
- **Kitchen Counter Staff:** `staff@canteen.edu` / `Staff@123`
- **Student Flow:** Click "Register New Student" or sign in to browse menu, test cart, and place an order.

### 3. Update `ALLOWED_ORIGINS`
Once Vercel assigns your real production domain (e.g. `https://canteen-os-jeremy.vercel.app`):
1. Go to **Vercel Dashboard $\rightarrow$ Settings $\rightarrow$ Environment Variables**.
2. Update `ALLOWED_ORIGINS` with your assigned URL.
3. Trigger a Redeploy under the **Deployments** tab.

---

## 5. Troubleshooting & Error Identification

| Issue | Manifestation | Root Cause & Resolution |
| :--- | :--- | :--- |
| **Database Connection Failure** | `/api/health` reports `"database": "disconnected"` or HTTP 500 on login. | Missing `?sslmode=require` or incorrect credentials in `DATABASE_URL`. Ensure you copied the **Pooled** connection string from Neon. |
| **CORS Blocked** | Browser console: `Access to fetch at ... has been blocked by CORS policy`. | The origin in browser address bar does not match any entry in `ALLOWED_ORIGINS`. Add your domain to `ALLOWED_ORIGINS` in Vercel settings and redeploy. |
| **404 on Subpages** | Direct URL navigation (e.g. `/menu`) shows 404. | Handled automatically by `vercel.json` rewrites. Ensure `vercel.json` is committed at the project root. |
| **JWT Session Expired** | Immediate logout or 401 error. | Automatic refresh token rotation is built-in (`/api/auth/refresh`). If `SECRET_KEY` was changed between deploys, existing sessions must re-login. |
