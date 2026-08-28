/**
 * Digital Canteen Token System - Main App Lifecycle
 */

const App = {
    init: function() {
        // Enforce permanent clean light mode
        localStorage.removeItem('canteen_theme');
        document.documentElement.removeAttribute('data-theme');
        this.renderNavbarUser();
        this.checkActiveBroadcasts();
    },

    renderNavbarUser: function() {
        const user = Auth.getUser();
        const navAuthSlot = document.getElementById('nav-auth-slot');
        if (!navAuthSlot) return;

        if (user) {
            navAuthSlot.innerHTML = `
                <div style="display:flex; align-items:center; gap:0.75rem;">
                    <div style="position:relative;">
                        <button class="btn btn-icon btn-outline btn-sm" onclick="NotificationsManager.toggleDropdown()" title="Notifications">
                            🔔 <span id="notif-badge" class="badge badge-accent" style="display:none; font-size:0.65rem; padding:0.15rem 0.4rem; position:absolute; top:-5px; right:-5px;">0</span>
                        </button>
                    </div>
                    <a href="/profile.html" class="btn btn-sm btn-secondary" style="font-weight:700;">
                        👤 ${user.name.split(' ')[0]}
                    </a>
                    ${Auth.isAdmin() ? `<a href="/admin/index.html" class="btn btn-sm btn-outline">⚡ Admin</a>` : ''}
                    <button class="btn btn-sm btn-danger" onclick="Auth.logout()">Logout</button>
                </div>
            `;
            NotificationsManager.fetchUnreadCount();
        } else {
            navAuthSlot.innerHTML = `
                <div style="display:flex; align-items:center; gap:0.75rem;">
                    <a href="/login.html" class="btn btn-sm btn-secondary">Login</a>
                    <a href="/register.html" class="btn btn-sm btn-primary">Sign Up</a>
                </div>
            `;
        }
    },

    checkActiveBroadcasts: async function() {
        if (!Auth.isAuthenticated()) return;
        const bannerContainer = document.getElementById('site-broadcast-container');
        if (!bannerContainer) return;

        try {
            const notifs = await ApiClient.get(CONFIG.ENDPOINTS.NOTIFICATIONS.MY);
            const activePromo = notifs.find(n => n.type === 'announcement' && !n.is_read);
            if (activePromo) {
                bannerContainer.innerHTML = `
                    <div class="broadcast-banner">
                        <div>
                            <strong>📢 ${activePromo.title}:</strong> ${activePromo.message}
                        </div>
                        <button class="broadcast-banner-close" onclick="App.dismissBroadcast(${activePromo.id})">✕</button>
                    </div>
                `;
            }
        } catch (e) {}
    },

    dismissBroadcast: async function(notifId) {
        try {
            await ApiClient.put(CONFIG.ENDPOINTS.NOTIFICATIONS.MARK_READ(notifId));
            const banner = document.getElementById('site-broadcast-container');
            if (banner) banner.innerHTML = '';
        } catch (e) {}
    }
};

window.App = App;

document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
