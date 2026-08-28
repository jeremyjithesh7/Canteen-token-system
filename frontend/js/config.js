/**
 * Digital Canteen Token System - Dynamic Frontend Configuration
 * Clean Split Architecture: Static Frontend (Vercel) + Persistent FastAPI API (Render)
 */

// ==============================================================================
// ⚡ PRODUCTION BACKEND URL CONFIGURATION (EDIT LINE 8 AFTER RENDER DEPLOYMENT)
// Replace the placeholder below with your live Render Web Service URL.
// Example: const RENDER_BACKEND_URL = 'https://canteen-os-backend.onrender.com';
// ==============================================================================
const RENDER_BACKEND_URL = 'https://REPLACE_WITH_RENDER_URL.onrender.com';

function resolveApiBaseUrl() {
    // 1. Explicit runtime override via window object or localStorage (useful for debugging)
    if (typeof window !== 'undefined' && window.CANTEEN_API_BASE) {
        return window.CANTEEN_API_BASE.replace(/\/+$/, '');
    }
    if (typeof localStorage !== 'undefined') {
        const stored = localStorage.getItem('canteen_api_base');
        if (stored) return stored.replace(/\/+$/, '');
    }

    // 2. Local development static servers automatically connect to local FastAPI backend
    if (typeof window !== 'undefined' && window.location) {
        const hostname = window.location.hostname;
        const port = window.location.port;
        if (
            (hostname === 'localhost' || hostname === '127.0.0.1') &&
            port &&
            port !== '8000' &&
            port !== ''
        ) {
            return 'http://127.0.0.1:8000';
        }
    }

    // 3. Standalone production deployment (Vercel, custom domain) -> calls Render backend
    return RENDER_BACKEND_URL.replace(/\/+$/, '');
}

const CONFIG = {
    API_BASE_URL: resolveApiBaseUrl(),

    ENDPOINTS: {
        AUTH: {
            REGISTER: '/api/auth/register',
            LOGIN: '/api/auth/login',
            REFRESH: '/api/auth/refresh',
            LOGOUT: '/api/auth/logout',
            ME: '/api/auth/me'
        },
        COUNTERS: {
            LIST: '/api/counters/',
            DETAIL: (id) => `/api/counters/${id}`
        },
        FOOD: {
            CATEGORIES: '/api/food/categories',
            ITEMS: '/api/food/items',
            ITEM_DETAIL: (id) => `/api/food/items/${id}`
        },
        ORDERS: {
            CREATE: '/api/orders/',
            MY_ORDERS: '/api/orders/me',
            DETAIL: (id) => `/api/orders/${id}`,
            ALL_ADMIN: '/api/orders/admin/all'
        },
        TOKENS: {
            ACTIVE_ME: '/api/tokens/active/me',
            LIVE_BOARD: '/api/tokens/live-board',
            DETAIL: (id) => `/api/tokens/${id}`,
            UPDATE_STATUS: (id) => `/api/tokens/${id}/status`
        },
        INVENTORY: {
            LIST: '/api/inventory/',
            RESTOCK: (food_id) => `/api/inventory/restock/${food_id}`,
            LOGS: '/api/inventory/logs'
        },
        AI: {
            RECOMMENDATIONS: '/api/ai/recommendations',
            DEMAND_FORECAST: '/api/ai/demand-forecast',
            DEMAND_OVERRIDE: '/api/ai/demand-override',
            DEMAND_OVERRIDES: '/api/ai/demand-overrides',
            DEMAND_VS_ACTUAL: '/api/ai/demand-vs-actual',
            QUEUE_STATUS: '/api/ai/queue-status',
            CROWD_FORECAST: '/api/ai/crowd-forecast',
            INVENTORY_INTELLIGENCE: '/api/ai/inventory-intelligence',
            WASTE_ANALYTICS: '/api/ai/waste-analytics',
            TRAFFIC_FORECAST: '/api/ai/traffic-forecast'
        },
        WALLET: {
            ME: '/api/wallet/me',
            TOPUP: '/api/wallet/topup'
        },
        REWARDS: {
            ME: '/api/rewards/me',
            LEADERBOARD: '/api/rewards/leaderboard'
        },
        NOTIFICATIONS: {
            MY: '/api/notifications/',
            MARK_READ: (id) => `/api/notifications/${id}/read`,
            BROADCAST: '/api/notifications/broadcast'
        },
        ADMIN: {
            DASHBOARD_STATS: '/api/admin/dashboard-stats',
            EXPORT_SALES: '/api/admin/export-sales',
            USERS: '/api/users/'
        }
    }
};

window.CONFIG = CONFIG;
