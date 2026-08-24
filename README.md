# ⚡ Digital Canteen Token System (Canteen OS)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.8-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg?logo=python)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?logo=postgresql)](https://www.postgresql.org)
[![Tests](https://img.shields.io/badge/Tests-38%20Passing-success.svg)](https://pytest.org)
[![Theme](https://img.shields.io/badge/UI%20Theme-Purple%20Neon-b026ff.svg)](https://github.com)

An end-to-end, production-grade smart college canteen ordering, multi-counter scheduling, and AI intelligence platform. Featuring a modern **Purple Neon Cyberpunk UI**, 25 authentic South Indian dishes with distinct high-quality food photography, dedicated cart & pre-ordering, customer dish ratings & reviews, big-screen TV kiosk display board, signature glowing token cards, in-browser vector QR generation, interactive Chart.js analytics, 7-day demand forecasting with admin overrides, rotating JWT refresh security, and multi-counter queue balancing.

---

## 🌟 Key Capabilities & Scale-Up Enhancements

### 🎨 Purple Neon Design System & Authentic South Indian Menu
- **Dark Neon Cyberpunk Aesthetics**: Deep cosmic violet canvas (`#0a0118`), elevated glass cards (`#140728`), neon electric purple (`#b026ff`), hot pink magenta (`#ff2ee6`), and cyan accents (`#00e5ff`).
- **Futuristic Typography**: Google Fonts `Space Grotesk` (clean readability) and `Orbitron` (high-tech display headers & token sequence numbers).
- **25 Authentic South Indian Dishes with 100% Unique Photos**:
  1. **South Indian Tiffin & Meals (Counter 1)**: Masala Dosa, Plain Dosa, Rava Dosa, Steamed Idlis, Crispy Medu Vada, Onion Tomato Uttapam, Ven Pongal, Rava Upma, Sambar Rice, Curd Rice, Bisi Bele Bath, Lemon Rice.
  2. **Traditional Desserts (Counter 2)**: Semiya Payasam, Desi Ghee Mysore Pak, Rava Kesari, Warm Gulab Jamun, Badam Halwa, Saffron Jalebi.
  3. **Beverages & Cafe Brews (Counter 3)**: Degree Filter Coffee, Masala Chai, Spiced Buttermilk (Majjige), Tender Coconut Water, Rose Milk, Malabar Sulaimani, Fresh Lime Soda.
- **Image Integrity Guarantee**: Automated test suite enforces zero duplicate images, non-empty URLs, and verified HTTP 200 resolution across all 25 dishes.

### 🛒 Dedicated Cart & Pre-Ordering Engine (`cart.html`)
- **Real-Time Persistent Cart**: Full database-synced cart session with localStorage offline resilience.
- **5% Canteen GST & Itemized Billing**: Accurate live tax computations and student discount deductions.
- **Scheduled Pre-Ordering**: Select pickup slots (*Immediate/ASAP, In 30 mins, Lunch Slot, Evening Snacks, Dinner Slot*).
- **Payment Method Selection**: Instant UPI (GPay/PhonePe/Paytm), Student Campus Wallet, Debit/Credit Card, and Cash at Billing Counter.

### 📺 Live Queue Tracker (`queue.html`) & Big-Screen Kiosk TV Display (`kiosk.html`)
- **Student Queue Tracker**: Live crowd meter (*Low, Moderate, High, Peak Rush*), average wait times, active order counters, and daily rush hour timetables.
- **Counter Big-Screen TV Kiosk (`kiosk.html`)**: High-contrast TV board display showing **Now Serving** and **Next Up** tokens across Counters 1, 2, and 3 with synthesized Web Audio API chime alerts on new token calls.

### ⭐ Customer Ratings & Dish Feedback (`orders.html` & `food_ratings`)
- **Interactive 5-Star Reviews**: Students can rate dishes directly from their order history and leave review comments.
- **Live Average Scores**: Menu cards render computed average star ratings and review counts dynamically.

### 🏢 Multi-Counter Kitchen Architecture
- **Counter 1 (`C1`)**: South Indian Tiffin & Rice Meals.
- **Counter 2 (`C2`)**: Desserts & Traditional Sweets.
- **Counter 3 (`C3`)**: Beverages & Cafe Bar.
- **Station-Scoped Token Allocation**: Automatically generates prefixed tokens (e.g. `C1-102`, `C2-201`, `C3-301`) to eliminate kitchen bottlenecks.

### 🛡️ Security, Rate Limiting & Session Continuity
- **Login Rate Limiter**: Thread-safe in-memory rate limiting defense allowing 5 failed attempts per 5 minutes before locking for 15 minutes with HTTP 429.
- **Refresh Token Rotation**: Short-lived JWT access tokens (30 min) paired with 7-day rotating refresh tokens (`/api/auth/refresh`) and logout invalidation (`/api/auth/logout`).
- **Structured Request Logging**: `RequestLoggingMiddleware` outputting timestamped JSON logs to `logs/canteen_requests.log` with sensitive fields masked.

### 🤖 AI Demand Intelligence & Overrides
- **7-Day Demand Forecasting**: Item-by-item next-day demand prediction with safety buffers and confidence bounds.
- **Predicted vs. Actual Accuracy (Chart.js)**: Interactive 7-day model accuracy benchmark comparing statistical predictions against actual recorded sales.
- **Manual Preparation Overrides**: Kitchen staff can adjust AI targets with auditable reasons and historical logs.
- **Explainable Food Recommendations**: Transparent, human-readable rationale badges based on order history, time slot, and macros.

---

## 📁 Project Structure

```
mini project/
├── frontend/                     # Modern Purple Neon Web Client
│   ├── index.html                # Landing page with live crowd metrics
│   ├── login.html                # Sign-in with 1-click demo logins
│   ├── register.html             # Student account registration
│   ├── dashboard.html            # Student portal with active token card & recs
│   ├── menu.html                 # 25 South Indian dishes with star ratings
│   ├── cart.html                 # Dedicated Cart with pre-ordering & GST calculation
│   ├── orders.html               # Order history with filters, reorder & rating modal
│   ├── token.html                # Live digital token tracker with vector QR
│   ├── queue.html                # Live queue depth & crowd density tracker
│   ├── kiosk.html                # Big-Screen Counter TV Display Board with audio chime
│   ├── profile.html              # Account & dietary preferences
│   ├── admin/                    # Admin Management Portal
│   │   ├── index.html            # Overview with Chart.js revenue & peak charts
│   │   ├── orders.html           # Live Kanban board with counter filter
│   │   ├── menu.html             # Dish catalog & counter assignment
│   │   ├── inventory.html        # Real-time stock & restock modal
│   │   ├── analytics.html        # AI Predicted vs Actual chart & overrides
│   │   ├── users.html            # User directory & loyalty tiers
│   │   └── notifications.html    # Site-wide broadcast announcement composer
│   ├── css/                      # Purple Neon Design Tokens & Styles
│   │   ├── style.css             # Colors, typography, buttons, inputs
│   │   ├── components.css        # Glowing token ticket, badges, skeletons
│   │   ├── animations.css        # Keyframe glows & motion-reduced fallbacks
│   │   └── admin.css             # Admin metrics, Kanban lanes, Chart containers
│   └── js/                       # Modular ES6+ Client Logic
│       ├── config.js             # API base URL & endpoints
│       ├── api.js                # Authenticated fetch wrapper with token refresh
│       ├── auth.js               # User auth, refresh rotation & loyalty sync
│       ├── cart.js               # Cart state, checkout & counter allocation
│       ├── token.js              # Live token poller, glowing ticket & audio chimes
│       ├── qr.js                 # Standalone vector QR code renderer
│       ├── admin.js              # Chart.js visualizers, Kanban & CSV exporter
│       ├── notifications.js      # Toast notifications & dropdown manager
│       └── app.js                # Navbar loyalty badge, broadcast banner & theme
│
├── backend/app/                  # Production FastAPI Application
│   ├── authentication/           # JWT access/refresh, rate limiting & deps
│   ├── database/                 # SQLAlchemy engine & session management
│   ├── models/                   # 22 Relational Models (Ratings, Cart, Counters, Overrides)
│   ├── schemas/                  # Pydantic v2 validation models
│   ├── services/                 # Business logic (Auth, Cart, Ratings, Tokens, AI)
│   ├── routes/                   # Modular API routers (Cart, Ratings, Kiosk, Orders)
│   ├── utils/                    # Structured JSON logger & rich startup seeder
│   └── main.py                   # FastAPI ASGI entrypoint & lifespan seeder
│
├── ai/                           # AI & Analytics Engines
│   ├── demand_prediction/        # Statistical regression model with override injection
│   ├── token_allocation/         # Multi-counter token allocator & queue scheduler
│   ├── food_recommendation/      # Context-aware explainable recommender
│   └── queue_prediction/         # M/M/c queue crowd level & wait predictor
│
├── database/                     # Database Schema & Seed Assets
│   ├── schema.sql                # Complete 22-table PostgreSQL schema
│   └── seed.sql                  # 25 unique South Indian dish photos & ratings
│
├── tests/                        # 38 Automated Test Suites (100% Pass Rate)
│   ├── conftest.py               # In-memory test database & auth fixtures
│   ├── ai/                       # AI model unit tests
│   ├── backend/                  # API endpoints, image integrity, cart, ratings, kiosk tests
│   └── frontend/                 # Frontend asset integrity tests
│
└── docs/                         # Technical Documentation
    ├── architecture.md           # Architecture diagrams & component breakdown
    ├── api-documentation.md      # REST API reference
    ├── database-design.md        # Database schema & entity relationships
    └── setup.md                  # Setup & deployment instructions
```

---

## 🚀 Quickstart Guide

### 1. Backend Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server (Auto-seeds database on startup)
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Client
```bash
# In a separate terminal
python3 -m http.server 3000 --directory frontend
```
Navigate to **`http://localhost:3000`** in your browser.

---

## 🧪 Automated Test Suite

Run the full test suite across all AI, backend, image integrity, and frontend subsystems:
```bash
./venv/bin/pytest -v tests/
```
Output:
```
======================= 38 passed in 2.88s =======================
```

---

## 🔑 Demo Login Credentials

| Role | Email | Password | Key Permissions |
|---|---|---|---|
| **Student** | `student@canteen.edu` | `Student@123` | Order food, cart checkout, track live QR token, rate dishes |
| **Kitchen Staff** | `staff@canteen.edu` | `Staff@123` | Advance tokens in Kanban lanes, view station queue |
| **Admin** | `admin@canteen.edu` | `Admin@123` | Full portal: revenue charts, demand overrides, CSV export |
