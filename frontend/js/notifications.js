/**
 * Digital Canteen Token System - Notification & Toast Manager
 */

class Toast {
    static init() {
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            document.body.appendChild(container);
        }
    }

    static show(message, type = 'info', duration = 3500) {
        this.init();
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let icon = 'ℹ️';
        if (type === 'success') icon = '✅';
        if (type === 'error') icon = '❌';
        if (type === 'warning') icon = '⚠️';

        toast.innerHTML = `
            <span style="font-size: 1.25rem">${icon}</span>
            <div style="flex: 1; font-size: 0.9rem; font-weight: 500;">${message}</div>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    static success(msg) { this.show(msg, 'success'); }
    static error(msg) { this.show(msg, 'error'); }
    static info(msg) { this.show(msg, 'info'); }
    static warning(msg) { this.show(msg, 'warning'); }
}

class NotificationsManager {
    static async updateBadge() {
        if (!Auth.isAuthenticated()) return;
        try {
            const res = await ApiClient.get(CONFIG.ENDPOINTS.NOTIFICATIONS.UNREAD_COUNT);
            const count = res.unread_count || 0;
            const badges = document.querySelectorAll('.notif-badge-count');
            badges.forEach(b => {
                b.textContent = count;
                b.style.display = count > 0 ? 'inline-flex' : 'none';
            });
        } catch (e) {
            // Silently ignore if network offline
        }
    }

    static async renderDropdown(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        try {
            const list = await ApiClient.get(CONFIG.ENDPOINTS.NOTIFICATIONS.LIST);
            if (!list || list.length === 0) {
                container.innerHTML = `<div style="padding: 1.5rem; text-align: center; color: var(--text-muted);">No new notifications</div>`;
                return;
            }

            container.innerHTML = list.map(item => `
                <div class="card" style="margin-bottom: 0.75rem; padding: 1rem; border-left: 3px solid ${item.is_read ? 'var(--border)' : 'var(--primary)'}; background: ${item.is_read ? 'var(--bg-input)' : 'var(--bg-card)'}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.25rem;">
                        <h4 style="font-size:0.95rem; font-weight:700;">${item.title}</h4>
                        <span style="font-size:0.75rem; color:var(--text-muted);">${new Date(item.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                    </div>
                    <p style="font-size:0.85rem; color:var(--text-secondary); margin-bottom: 0.5rem;">${item.message}</p>
                    ${!item.is_read ? `<button class="btn btn-sm btn-outline" onclick="NotificationsManager.markRead(${item.id})">Mark as Read</button>` : ''}
                </div>
            `).join('');
        } catch (e) {
            container.innerHTML = `<div style="padding: 1rem; color: var(--danger)">Failed to load notifications.</div>`;
        }
    }

    static async markRead(id) {
        try {
            await ApiClient.put(CONFIG.ENDPOINTS.NOTIFICATIONS.MARK_READ(id));
            this.updateBadge();
            const el = document.getElementById('notifications-list');
            if (el) this.renderDropdown('notifications-list');
        } catch (e) {
            console.error(e);
        }
    }
}

window.Toast = Toast;
window.NotificationsManager = NotificationsManager;
