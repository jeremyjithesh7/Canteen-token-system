/**
 * Digital Canteen Token System - API Client
 * Centralized Fetch wrapper with automatic JWT injection, error handling, and refresh token rotation.
 */

class ApiClient {
    static getBaseUrl() {
        if (typeof CONFIG !== 'undefined' && typeof CONFIG.API_BASE_URL === 'string') {
            return CONFIG.API_BASE_URL;
        }
        return '';
    }

    static async request(endpoint, options = {}) {
        const baseUrl = ApiClient.getBaseUrl();
        const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };

        const token = localStorage.getItem('canteen_token');
        if (token && !headers['Authorization']) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);

            // Handle 401 Unauthorized with automatic refresh token attempt
            if (response.status === 401 && !options._isRetry && localStorage.getItem('canteen_refresh_token')) {
                if (typeof Auth !== 'undefined' && Auth.tryRefreshToken) {
                    const refreshed = await Auth.tryRefreshToken();
                    if (refreshed) {
                        options._isRetry = true;
                        return ApiClient.request(endpoint, options);
                    } else {
                        if (Auth.logout) Auth.logout();
                        throw new Error('Session expired. Please log in again.');
                    }
                }
            }

            if (response.status === 204) {
                return null;
            }

            // Check if response is file download
            const disposition = response.headers.get('Content-Disposition');
            if (disposition && disposition.includes('attachment')) {
                return response.blob();
            }

            const data = await response.json();

            if (!response.ok) {
                const errorMsg = data.detail || (typeof data === 'string' ? data : 'API Request Failed');
                throw new Error(errorMsg);
            }

            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    static get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return ApiClient.request(url, { method: 'GET' });
    }

    static post(endpoint, body = {}) {
        return ApiClient.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(body)
        });
    }

    static put(endpoint, body = {}) {
        return ApiClient.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(body)
        });
    }

    static delete(endpoint) {
        return ApiClient.request(endpoint, { method: 'DELETE' });
    }
}

window.ApiClient = ApiClient;
window.API = ApiClient;

window.showNotification = function(msg, type = "info") {
    const existing = document.getElementById("canteen-toast-notif");
    if (existing) existing.remove();

    const toast = document.createElement("div");
    toast.id = "canteen-toast-notif";
    toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        background: ${type === 'success' ? 'rgba(0, 229, 255, 0.95)' : (type === 'error' ? 'rgba(255, 0, 85, 0.95)' : 'rgba(176, 38, 255, 0.95)')};
        color: ${type === 'success' ? '#0a0118' : '#ffffff'};
        padding: 0.85rem 1.4rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.95rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        z-index: 99999;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.3s ease;
        backdrop-filter: blur(8px);
    `;
    toast.innerHTML = `<span>${type === 'success' ? '✅' : (type === 'error' ? '⚠️' : '⚡')}</span> <span>${msg}</span>`;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(10px)";
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};
