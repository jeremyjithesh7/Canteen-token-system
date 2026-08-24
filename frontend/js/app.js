/**
 * Digital Canteen Token System - Main App Lifecycle & Theme Switcher
 */

const App = {
    init: function() {
        this.initTheme();
        this.renderNavbarUser();
        this.checkActiveBroadcasts();
    },

    initTheme: function() {
        const savedTheme = localStorage.getItem('canteen_theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
        this.updateThemeToggleIcon(savedTheme);
    },

    toggleTheme: function() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('canteen_theme', newTheme);
        this.updateThemeToggleIcon(newTheme);
    },

    updateThemeToggleIcon: function(theme) {
        const btns = document.querySelectorAll('.theme-toggle-btn');
        btns.forEach(btn => {
            btn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
            btn.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
        });
    },

    renderNavbarUser: function() {
        const user = Auth.getUser();
        const navAuthSlot = document.getElementById('nav-auth-slot');
        if (!navAuthSlot) return;

        if (user) {
            navAuthSlot.innerHTML = `
                <div style="display:flex; align-items:center; gap:0.75rem;">
                    <div class="loyalty-badge-pill" title="Your Canteen Loyalty Level">
                        ${user.loyalty_badge || '🌱 New Explorer'}
                    </div>
                    <button class="theme-toggle-btn" onclick="App.toggleTheme()" title="Toggle Theme">☀️</button>
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
                    <button class="theme-toggle-btn" onclick="App.toggleTheme()" title="Toggle Theme">☀️</button>
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
