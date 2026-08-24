/**
 * Digital Canteen Token System - Authentication & Session Management
 */

const Auth = {
    getToken: function() {
        return localStorage.getItem('canteen_token');
    },

    getRefreshToken: function() {
        return localStorage.getItem('canteen_refresh_token');
    },

    getUser: function() {
        const userStr = localStorage.getItem('canteen_user');
        try {
            return userStr ? JSON.parse(userStr) : null;
        } catch (e) {
            return null;
        }
    },

    isAuthenticated: function() {
        return !!this.getToken();
    },

    isLoggedIn: function() {
        return !!this.getToken();
    },

    isAdmin: function() {
        const user = this.getUser();
        return user && (user.role_id === 1 || (user.role && user.role.name === 'admin'));
    },

    isStaffOrAdmin: function() {
        const user = this.getUser();
        return user && (user.role_id === 1 || user.role_id === 2 || (user.role && (user.role.name === 'admin' || user.role.name === 'staff')));
    },

    setSession: function(data) {
        if (data.access_token) {
            localStorage.setItem('canteen_token', data.access_token);
        }
        if (data.refresh_token) {
            localStorage.setItem('canteen_refresh_token', data.refresh_token);
        }
        if (data.user) {
            localStorage.setItem('canteen_user', JSON.stringify(data.user));
        }
    },

    tryRefreshToken: async function() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) return false;
        try {
            const baseUrl = typeof CONFIG !== 'undefined' ? CONFIG.API_BASE_URL : 'http://127.0.0.1:8000';
            const endpoint = (typeof CONFIG !== 'undefined' && CONFIG.ENDPOINTS && CONFIG.ENDPOINTS.AUTH) ? CONFIG.ENDPOINTS.AUTH.REFRESH : '/api/auth/refresh';
            const res = await fetch(`${baseUrl}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken })
            });
            if (res.ok) {
                const data = await res.json();
                this.setSession(data);
                return true;
            }
        } catch (e) {
            console.error('Failed to refresh token:', e);
        }
        return false;
    },

    login: async function(email, password) {
        try {
            const endpoint = (typeof CONFIG !== 'undefined' && CONFIG.ENDPOINTS && CONFIG.ENDPOINTS.AUTH) ? CONFIG.ENDPOINTS.AUTH.LOGIN : '/api/auth/login';
            const data = await ApiClient.post(endpoint, { email, password });
            this.setSession(data);
            return data;
        } catch (error) {
            throw error;
        }
    },

    register: async function(userData) {
        try {
            const data = await ApiClient.post(CONFIG.ENDPOINTS.AUTH.REGISTER, userData);
            this.setSession(data);
            return data;
        } catch (error) {
            throw error;
        }
    },

    logout: async function() {
        const refreshToken = this.getRefreshToken();
        if (refreshToken) {
            try {
                await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.AUTH.LOGOUT}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ refresh_token: refreshToken })
                });
            } catch (e) {}
        }
        localStorage.removeItem('canteen_token');
        localStorage.removeItem('canteen_refresh_token');
        localStorage.removeItem('canteen_user');
        window.location.href = '/login.html';
    },

    requireAuth: function() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login.html';
        }
    },

    requireAdmin: function() {
        if (!this.isAuthenticated() || !this.isAdmin()) {
            window.location.href = '/login.html';
        }
    },

    requireStaffOrAdmin: function() {
        if (!this.isAuthenticated() || !this.isStaffOrAdmin()) {
            window.location.href = '/login.html';
        }
    },

    syncUserLoyalty: async function() {
        if (!this.isAuthenticated()) return null;
        try {
            const user = await ApiClient.get(CONFIG.ENDPOINTS.AUTH.ME);
            if (user) {
                localStorage.setItem('canteen_user', JSON.stringify(user));
                return user;
            }
        } catch (e) {}
        return this.getUser();
    }
};

window.Auth = Auth;
