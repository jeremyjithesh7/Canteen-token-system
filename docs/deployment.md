# 🚀 Production Deployment Guide - CanteenOS (Render + Vercel + Neon PostgreSQL)

This document is the verified production deployment manual for **CanteenOS**. It details the exact clean split architecture, configuration steps, and verification procedures.

---

## 1. Target Architecture Overview

```
Vercel  →  Serves ONLY frontend/ as a static site. No backend code, no API routing, no Python.
Render  →  Runs ONLY the backend as a persistent FastAPI web service (uvicorn), reachable at its own URL.
Neon    →  PostgreSQL database with connection pooling. Backend connects via DATABASE_URL.
```

- **Frontend (`frontend/` on Vercel):** Pure vanilla HTML5, CSS3, and ES6+ JavaScript. Served globally via Vercel's Edge CDN. Configured with clean URL rewrites.
- **Backend API (`backend/` on Render):** Persistent FastAPI service running with `uvicorn` on Python 3.12, binding to `0.0.0.0:$PORT`.
- **Database (Neon PostgreSQL):** Cloud PostgreSQL with PgBouncer connection pooling.
- **Cross-Domain Communication:** The frontend communicates directly with the backend via CORS using the full Render URL (e.g. `https://canteen-os-backend.onrender.com`).

---

## 2. Step 1: Database Setup (Neon PostgreSQL) [ALREADY REUSED]

1. Log in to **[neon.tech](https://neon.tech)**.
2. Select your project (e.g. `canteen-os-prod`).
3. In the Dashboard under **Connection Details**:
   - Enable the **"Pooled connection"** checkbox (`-pooler` in the host domain).
   - Copy the connection string.
4. **Format Verification:**
   ```text
   postgresql://[user]:[password]@ep-[name]-pooler.[region].aws.neon.tech/[dbname]?sslmode=require
   ```

---

## 3. Step 2: Render Backend Web Service Setup

### Option A: Using `render.yaml` (Render Blueprint)
1. Push the repo to GitHub.
2. In Render Dashboard, click **New +** $\rightarrow$ **Blueprint**.
3. Connect your repository. Render will automatically detect `render.yaml`.
4. Provide the secret `DATABASE_URL` when prompted.

### Option B: Manual Web Service Creation in Render Dashboard
If configuring manually:
- **Service Type:** Web Service
- **Environment:** `Python 3`
- **Root Directory:** *(leave blank for repo root)*
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path:** `/api/health`

### Environment Variables on Render:

| Variable Name | Example / Recommended Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://user:pass@ep-...-pooler.../dbname?sslmode=require` | Pooled Neon PostgreSQL connection string |
| `SECRET_KEY` | *(Run `openssl rand -hex 32`)* | Cryptographic JWT signing secret (min 32 bytes) |
| `ALLOWED_ORIGINS` | `http://localhost:3000,https://REPLACE_WITH_VERCEL_URL.vercel.app` | Allowed CORS origins (add your Vercel URL) |
| `ENV` | `production` | Declares production environment |
| `DEBUG` | `false` | Disables debug stack traces |
| `PYTHON_VERSION` | `3.12.8` | Pinned Python runtime version |
| `UPI_VPA` | `canteen@upi` | **OVERRIDE DEFAULT** (demo UPI ID) |
| `UPI_PAYEE_NAME` | `Campus Canteen Services` | **OVERRIDE DEFAULT** (canteen name) |
| `UPI_MERCHANT_CODE` | `5812` | Food & Canteen merchant category code |
| `CAMPUS_GST_PERCENT`| `5.0` | Campus GST percentage |

> [!WARNING]
> **UPI Credentials Notice:** Code-level defaults in `backend/app/config.py` contain developer demo values (`jeremyjithesh7@oksbi`). You must explicitly set `UPI_VPA="canteen@upi"` and `UPI_PAYEE_NAME="Campus Canteen Services"` in Render's environment variables.

---

## 4. Step 3: Frontend API URL Configuration

Once Render completes the initial deploy, copy your service URL (e.g., `https://canteen-os-backend.onrender.com`).

Edit **`frontend/js/config.js`** at **line 8**:
```javascript
const RENDER_BACKEND_URL = 'https://canteen-os-backend.onrender.com';
```

Commit and push this change to GitHub:
```bash
git add frontend/js/config.js
git commit -m "Update Render backend production URL"
git push origin main
```

---

## 5. Step 4: Vercel Frontend Deployment

1. Log in to **[vercel.com](https://vercel.com)** and click **"Add New Project"**.
2. Select your `Canteen-token-system` repository.
3. Configure Project Settings:
   - **Framework Preset:** `Other`
   - **Root Directory:** Click edit and set to `frontend/`
   - **Build Command:** *(leave empty — no build step needed)*
   - **Output Directory:** *(leave empty)*
4. Click **Deploy**.
5. Vercel will serve your static frontend with clean URL routing configured via `frontend/vercel.json`.

---

## 6. Step 5: CORS Finalization

1. Copy your live Vercel URL (e.g., `https://canteen-os-frontend.vercel.app`).
2. Go to **Render Dashboard** $\rightarrow$ your `canteen-os-backend` service $\rightarrow$ **Environment**.
3. Update `ALLOWED_ORIGINS` to include your Vercel URL:
   ```text
   ALLOWED_ORIGINS="https://canteen-os-frontend.vercel.app,http://localhost:3000"
   ```
4. Render will automatically redeploy with the updated CORS policy.

---

## 7. Step 6: End-to-End Live Verification Checklist

- [ ] Visit `https://<render-backend-url>/api/health` $\rightarrow$ Confirm `{"status": "healthy", "database": "connected"}`.
- [ ] Visit `https://<vercel-frontend-url>/login` $\rightarrow$ Page loads without console errors.
- [ ] Log in as Admin (`admin@canteen.edu` / `Admin@123`) $\rightarrow$ Verify dashboard metrics and menu load.
- [ ] Log in as Staff (`staff@canteen.edu` / `Staff@123`) $\rightarrow$ Open `/verify` page.
- [ ] Register a new student account $\rightarrow$ Browse menu (confirm all 25 food images load) $\rightarrow$ Add to cart $\rightarrow$ Checkout $\rightarrow$ Token generation.
- [ ] Check `/kiosk` $\rightarrow$ Confirm live order board updates.
