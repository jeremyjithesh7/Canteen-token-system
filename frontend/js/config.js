/**
 * Digital Canteen Token System - Frontend Configuration & Endpoints
 */

const CONFIG = {
    API_BASE_URL: 'http://127.0.0.1:8000',

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
