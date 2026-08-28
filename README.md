# ⚡ CanteenOS - Digital Canteen Token & Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.8-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon%20Serverless-336791.svg?logo=postgresql)](https://neon.tech)
[![Vercel Ready](https://img.shields.io/badge/Vercel-Serverless%20Functions-black.svg?logo=vercel)](https://vercel.com)
[![Tests](https://img.shields.io/badge/Tests-71%20Passing-success.svg)](https://pytest.org)
[![Design](https://img.shields.io/badge/UI-Dark%20Glassmorphism-6366f1.svg)](https://github.com)

An end-to-end, production-ready campus canteen ordering, multi-counter scheduling, and kitchen intelligence platform. Built with **FastAPI**, **PostgreSQL** (with Neon serverless connection pooling and local SQLite fallback), **Serverless Vercel Functions**, and a **Dark Glassmorphic Web Client**.

---

## 🌟 Key Features & Architecture

### 🍽️ 25 Authentic South Indian Dishes & Station Load Balancing
- **Station-Scoped Allocation**:
  - **Counter 1 (`C1`)**: South Indian Tiffin & Rice Meals (Dosas, Idlis, Vadas, Pongal, Bisi Bele Bath, Sambar Rice).
  - **Counter 2 (`C2`)**: Desserts & Traditional Sweets (Payasam, Mysore Pak, Kesari, Gulab Jamun, Badam Halwa, Jalebi).
  - **Counter 3 (`C3`)**: Beverages & Cafe Brews (Filter Coffee, Masala Chai, Majjige, Tender Coconut Water, Sulaimani).
- **Nutritional Transparency**: Per-dish macros (calories, protein, carbohydrates, fats) and kitchen preparation time indicators.
- **Local High-Resolution Assets**: Dedicated curated dish photography bundled in `frontend/assets/menu/`.

### 💳 Real Payment Options & Financial Integrity
- **Campus Wallet**: Instant balance top-up and atomic order settlement with dedicated transaction ledger logging (`wallet_transactions`).
- **Real UPI Payment QR & Deep-Linking**: Dynamic UPI URI generation (`upi://pay?pa=...&am=...`) with scannable QR codes and a 12-digit UTR/transaction reference submission modal for accounting verification.
- **5% Campus GST**: Automatic server-side subtotal, tax computation, and discounts.

### 🎫 Live Token Tracking & Counter Staff Verification
- **Dynamic Digital Token Cards (`token.html`)**: Real-time ticket showing counter station, live status (`Waiting` $\rightarrow$ `Preparing` $\rightarrow$ `Ready` $\rightarrow$ `Completed`), dynamic turnaround wait estimation, queue position, and scannable QR tokens.
- **Staff QR Verification Module (`verify.html`)**: Counter operators can scan student phone QR codes or enter token strings (`C1-015`) to verify ordered items and prevent **duplicate food collection** with audio-visual alerts.
- **Big-Screen Kiosk TV Display (`kiosk.html`)**: High-contrast TV board display showing **Now Serving** and **Next Up** tokens across Counters 1, 2, and 3 with Web Audio chime alerts.
- **Live Queue View (`queue.html`)**: Public crowd meter (*Low, Moderate, High, Peak Rush*), active queue depth, and hourly rush timetables.

### 📊 Relational Database Inspector & Admin Portal
- **Database Live Inspector (`/admin/database.html`)**: Full administrative relational browser to view, search, and inspect live PostgreSQL records across all 27 tables (Users, Orders, Order Items, Tokens, Payments, Wallets, Inventory, Waste Logs, Ratings, and AI data).
- **Kitchen Kanban & Live Orders (`/admin/orders.html`)**: Real-time lane transitions per counter.
- **Inventory & Stock Alert Logs (`/admin/inventory.html`)**: Real-time stock counts with automated depletion on order placement and restock audit trails (`inventory_logs`).
- **Kitchen Food Waste Analytics (`/admin/waste.html`)**: Daily leftover and food waste tracking with financial loss impact computation.

### 🤖 Predictive Engines & Intelligence
- **Statistical Demand Forecasting**: Item-by-item next-day demand prediction with safety buffers, confidence bounds, and administrative manual overrides.
- **Adaptive Queue Wait Estimator**: Calculates queue wait time based on active counter load, dish preparation complexity, and hourly crowd profiles.
- **Context-Aware Dish Recommender**: Personalized suggestions combining past ordering frequency, meal slot (Breakfast, Lunch, Snacks, Dinner), and dietary constraints.

---

## 📁 Repository Structure

```
.
├── api/
│   └── index.py                  # Vercel Serverless Function entrypoint (FastAPI ASGI)
├── backend/
│   ├── app/
│   │   ├── authentication/       # JWT access/refresh token handlers & bcrypt hashing
│   │   ├── database/             # SQLAlchemy engine & session lifecycle (Postgres/SQLite)
│   │   ├── models/               # 27 Relational SQLAlchemy models
│   │   ├── routes/               # 16 Modular API routers (auth, orders, tokens, admin, db viewer, etc.)
│   │   ├── schemas/              # Pydantic v2 request/response validation schemas
│   │   ├── services/             # Core business logic (orders, wallet, rewards, tokens, AI)
│   │   ├── utils/                # Database seeding & logging middleware
│   │   ├── config.py             # Pydantic SettingsConfigDict with environment support
│   │   └── main.py               # FastAPI application definition & CORS configuration
│   ├── .env.example              # Environment variables template
│   └── requirements.txt          # Backend dependencies
├── database/
│   ├── schema.sql                # Production PostgreSQL DDL schema
│   ├── seed.sql                  # Initial seed dataset
│   └── reset_demo_data.sql       # Safe clean-slate reset script
├── docs/
│   ├── api-documentation.md      # API endpoint documentation
│   └── setup.md                  # Comprehensive setup & Vercel/Neon deployment guide
├── frontend/                     # Modern Dark Glassmorphic Web Client
│   ├── index.html                # Landing page with crowd metrics & quick actions
│   ├── menu.html                 # 25 South Indian dishes with category filters & macros
│   ├── cart.html                 # Persistent cart, schedule pre-order, and UPI/Wallet checkout
│   ├── orders.html               # Student order history & 5-star review modal
│   ├── token.html                # Live token tracker with scannable QR ticket
│   ├── verify.html               # Staff QR pickup scanner & duplicate prevention tool
│   ├── wallet.html               # Campus wallet balance, top-up, & transaction ledger
│   ├── rewards.html              # Loyalty tier progression, points, & streak badges
│   ├── kiosk.html                # Big-screen TV counter status board
│   ├── queue.html                # Public queue & crowd level dashboard
│   ├── ai-center.html            # AI demand forecasting, traffic trends, & recommendations
│   ├── admin/                    # Management portal
│   │   ├── index.html            # Revenue trends & peak hour charts
│   │   ├── orders.html           # Live kitchen status Kanban board
│   │   ├── menu.html             # Dish pricing, availability, and station editor
│   │   ├── inventory.html        # Real-time stock levels & restocking modal
│   │   ├── waste.html            # Food waste logging & cost analytics
│   │   ├── analytics.html        # Demand forecast benchmarks & override controls
│   │   ├── users.html            # User directory & role management
│   │   ├── notifications.html    # Site broadcast announcement composer
│   │   └── database.html         # Live Relational PostgreSQL Table Inspector
│   ├── css/                      # Design system (style.css, components.css, admin.css, animations.css)
│   ├── js/                       # Modular ES6+ client logic (config.js, api.js, auth.js, cart.js, token.js, admin.js)
│   └── assets/menu/              # 25 Curated South Indian food photos
├── tests/                        # 71 Automated pytest unit & integration tests
├── .env.example                  # Root environment variables template
├── .gitignore                    # Git exclusions (secrets, database files, bytecode)
├── .python-version               # Pinned to Python 3.12
├── requirements.txt              # Pinned root dependencies for Vercel deployment
└── vercel.json                   # Unified Vercel deployment routing configuration
```

---

## 🚀 Quick Start (Local Development)

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/jeremyjithesh7/Canteen-token-system.git
cd Canteen-token-system

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```
*(By default, `DATABASE_URL` will use local SQLite `sqlite:///./canteen.db` if unset, or you can point it to a local/remote PostgreSQL instance).*

### 3. Run the Backend API & Web Application
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open **`http://localhost:8000`** in your browser. FastAPI automatically serves the static frontend alongside the API.

---

## ☁️ Deployment on Vercel & Neon PostgreSQL

### 1. Database Setup (Neon Serverless PostgreSQL)
1. Create a free database at [neon.tech](https://neon.tech).
2. Copy the **Pooled Connection String** (format: `postgresql://user:pass@ep-sample-pooler.region.aws.neon.tech/dbname?sslmode=require`).

### 2. Deploy to Vercel (Unified Architecture)
1. Import this repository into [Vercel](https://vercel.com).
2. Set the following Environment Variables in Vercel Project Settings:
   - `DATABASE_URL`: Your Neon Pooled connection string.
   - `SECRET_KEY`: A secure 32-byte secret (`openssl rand -hex 32`).
   - `ALLOWED_ORIGINS`: `https://your-canteen-app.vercel.app`
   - `ENV`: `production`
   - `DEBUG`: `false`
3. Click **Deploy**. Vercel will automatically build the serverless functions (`api/index.py`) and host the static frontend via `vercel.json`.

---

## 🧪 Automated Testing

The repository contains 71 automated pytest unit and integration tests covering authentication, order placement, inventory logs, QR token verification, rating constraints, real UPI billing, rewards, and AI analytics.

```bash
./venv/bin/pytest -v
```

---

## 🔑 Default Operational Accounts

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@canteen.edu` | `Admin@123` | Full admin portal, revenue charts, demand overrides, database inspector |
| **Kitchen Staff** | `staff@canteen.edu` | `Staff@123` | Kitchen Kanban, order status management, QR token verification |
| **Student** | *(Register new student)* | *(Your password)* | Menu browsing, cart, wallet top-up, UPI payment, token tracking, reviews |

---

## 📄 License
This project is licensed under the MIT License.
