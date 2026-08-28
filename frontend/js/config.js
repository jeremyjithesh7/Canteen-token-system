/**
 * Digital Canteen Token System - Dynamic Frontend Configuration
 * Auto-detects local development vs. unified or external production backend.
 */

function resolveApiBaseUrl() {
    // 1. Explicit runtime override via window object or localStorage
    if (typeof window !== 'undefined' && window.CANTEEN_API_BASE) {
        return window.CANTEEN_API_BASE.replace(/\/+$/, '');
    }
    if (typeof localStorage !== 'undefined') {
        const stored = localStorage.getItem('canteen_api_base');
        if (stored) return stored.replace(/\/+$/, '');
    }

    // 2. Browser origin detection
    if (typeof window !== 'undefined' && window.location) {
        const port = window.location.port;
        const hostname = window.location.hostname;

        // Local development static servers (e.g. port 3000, 5500, 5173) connecting to local backend
        if (
            (hostname === 'localhost' || hostname === '127.0.0.1') &&
            port &&
            port !== '8000' &&
            port !== ''
        ) {
            return 'http://127.0.0.1:8000';
        }

        // Same-origin deployments (FastAPI static mount or Vercel unified deployment with /api routing)
        return '';
    }

    return '';
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
