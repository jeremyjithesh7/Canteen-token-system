# REST API Reference - Digital Canteen Token System

**Base URL:** `http://127.0.0.1:8000`  
**Interactive Swagger Docs:** `http://127.0.0.1:8000/docs`  
**OpenAPI Specification:** `http://127.0.0.1:8000/openapi.json`

---

## 1. Authentication & Security Endpoints (`/api/auth`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register` | Registers a new student account | None |
| `POST` | `/api/auth/login` | Authenticates user; returns access + refresh tokens (Rate-limited: 5 attempts/5m) | None |
| `POST` | `/api/auth/refresh` | Rotates refresh token & issues new access token | None |
| `POST` | `/api/auth/logout` | Revokes the active refresh token | Bearer Token |
| `GET` | `/api/auth/me` | Fetches current user profile with loyalty badge & stats | Bearer Token |

### Sample Login Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 2,
    "name": "Aarav Sharma",
    "email": "student@canteen.edu",
    "role_id": 3,
    "loyalty_tier": "VIP Legend",
    "loyalty_badge": "👑 VIP Legend",
    "total_orders_count": 24
  }
}
```

---

## 2. Counters & Station Management (`/api/counters`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/counters/` | Lists all active pickup counters (C1, C2, C3) | None |
| `GET` | `/api/counters/{id}` | Fetches details for a specific counter | None |
| `POST` | `/api/counters/` | Creates a new kitchen counter station | Admin |
| `PUT` | `/api/counters/{id}` | Updates counter status or station type | Admin |

---

## 3. Digital Tokens & Kitchen Queue (`/api/tokens`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/tokens/active/me` | Returns current user's active token ticket | Bearer Token |
| `GET` | `/api/tokens/my-tokens` | Returns complete token history for user | Bearer Token |
| `GET` | `/api/tokens/live-board` | Returns public queue board across all counters | None |
| `GET` | `/api/tokens/{id}` | Returns single token details | None |
| `PUT` | `/api/tokens/{id}/status`| Advances token state (`Waiting` → `Preparing` → `Ready` → `Completed`) | Staff / Admin |

---

## 4. AI Demand Intelligence & Overrides (`/api/ai`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/ai/recommendations` | Personalized food recommendations with explainability reasons | Bearer Token |
| `GET` | `/api/ai/demand-forecast` | Next-day statistical demand forecast with confidence bounds | Staff / Admin |
| `GET` | `/api/ai/demand-vs-actual` | 7-day predicted vs. recorded sales accuracy dataset for Chart.js | Staff / Admin |
| `POST` | `/api/ai/demand-override` | Creates manual prep override with audit logging | Staff / Admin |
| `GET` | `/api/ai/demand-overrides` | Retrieves full audit log of kitchen prep adjustments | Staff / Admin |
| `GET` | `/api/ai/queue-status` | Real-time crowd density, turnaround estimate, and counter loads | None |

---

## 5. Admin Command & Sales Export (`/api/admin`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/admin/dashboard-stats` | Aggregated revenue, today's orders, queue depth, and Chart.js series | Staff / Admin |
| `GET` | `/api/admin/export-sales` | Streams complete CSV sales report with item and counter breakdowns | Admin |
| `GET` | `/api/admin/users` | Lists all users with loyalty metrics and statuses | Admin |

---

## 6. Notifications & Broadcast Announcements (`/api/notifications`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/notifications/my` | Retrieves user notifications | Bearer Token |
| `POST` | `/api/notifications/broadcast` | Broadcasts site-wide announcement banner | Admin |
| `PUT` | `/api/notifications/{id}/read` | Marks notification as read | Bearer Token |
| `PUT` | `/api/notifications/read-all` | Marks all user notifications as read | Bearer Token |
