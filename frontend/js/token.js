/**
 * Smart Campus Canteen OS - Live Digital Token Tracker & Polling
 */

class TokenTracker {
    static initLiveTracking(tokenId, onUpdateCallback, intervalMs = 3500) {
        let lastStatus = null;

        const checkStatus = async () => {
            try {
                let tokenData;
                if (tokenId) {
                    tokenData = await ApiClient.get(CONFIG.ENDPOINTS.TOKENS.DETAIL(tokenId));
                } else {
                    tokenData = await ApiClient.get(CONFIG.ENDPOINTS.TOKENS.ACTIVE_ME);
                }

                if (tokenData) {
                    if (lastStatus && lastStatus !== tokenData.status && tokenData.status === 'Ready') {
                        this.playReadySound();
                        if (window.Toast) {
                            Toast.success(`🔔 TOKEN ${tokenData.token_number} IS READY! Collect at Counter ${tokenData.counter_number}`);
                        }
                    }
                    lastStatus = tokenData.status;

                    if (onUpdateCallback) {
                        onUpdateCallback(tokenData);
                    }
                } else if (onUpdateCallback) {
                    onUpdateCallback(null);
                }
            } catch (err) {
                console.warn('Token status poll error:', err);
                if (onUpdateCallback) {
                    onUpdateCallback(null);
                }
            }
        };

        // Initial check
        checkStatus();
        // Polling interval
        const timerId = setInterval(checkStatus, intervalMs);
        return () => clearInterval(timerId);
    }

    static renderSignatureCard(tokenData, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (!tokenData) {
            container.innerHTML = `
                <div class="card empty-state">
                    <div class="empty-state-icon"><i class="fa-solid fa-ticket"></i></div>
                    <h3 class="empty-state-title">No Active Digital Token</h3>
                    <p class="empty-state-desc">You don't have any waiting or preparing orders right now.</p>
                    <a href="/menu.html" class="btn btn-primary"><i class="fa-solid fa-utensils"></i> Browse Menu & Order</a>
                </div>
            `;
            return;
        }

        const statusClass = `badge-${tokenData.status.toLowerCase()}`;
        const qrPayload = JSON.stringify({
            token: tokenData.token_number,
            order_id: tokenData.order_id,
            counter: tokenData.counter_number,
            user_id: tokenData.user_id,
            issued_at: tokenData.created_at
        });

        container.innerHTML = `
            <div class="token-ticket-glow">
                <div class="token-ticket-inner">
                    <div class="token-header-meta">
                        <span style="font-size:0.75rem; color:var(--text-muted); font-weight:700; text-transform:uppercase; letter-spacing:0.04em;">Digital Token Ticket</span>
                        <span class="badge ${statusClass}">${tokenData.status}</span>
                    </div>

                    <div class="token-counter-pill">
                        <i class="fa-solid fa-store"></i> Pickup Counter ${tokenData.counter_number || 1}
                    </div>

                    <div style="font-size:0.75rem; color:var(--text-muted); text-transform:uppercase; font-weight:700; letter-spacing:0.04em;">Token Number</div>
                    <div class="token-number-hero">${tokenData.token_number}</div>

                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:var(--space-3); margin:var(--space-4) 0; text-align:left; background:var(--bg-surface); padding:var(--space-3) var(--space-4); border-radius:var(--radius-sm); border:1px solid var(--border);">
                        <div>
                            <span style="font-size:0.6875rem; color:var(--text-muted); display:block; text-transform:uppercase; font-weight:700;">Estimated Wait</span>
                            <strong style="font-size:1.05rem; color:var(--accent); font-family:var(--font-accent);">~${tokenData.estimated_wait_minutes} mins</strong>
                        </div>
                        <div>
                            <span style="font-size:0.6875rem; color:var(--text-muted); display:block; text-transform:uppercase; font-weight:700;">Queue Position</span>
                            <strong style="font-size:1.05rem; color:var(--primary-hover); font-family:var(--font-accent);">${tokenData.queue_position > 0 ? '#' + tokenData.queue_position + ' in line' : 'At Counter'}</strong>
                        </div>
                    </div>

                    <!-- Scannable QR Code -->
                    <div style="margin:var(--space-4) 0;">
                        <span style="font-size:0.75rem; color:var(--text-muted); display:block; margin-bottom:var(--space-2); text-transform:uppercase; font-weight:700; letter-spacing:0.04em;">Scannable QR for Staff Pickup</span>
                        <div id="token-qr-slot" style="display:flex; justify-content:center;"></div>
                    </div>

                    <div style="display:flex; justify-content:center; gap:var(--space-2); margin-top:var(--space-4);">
                        <a href="/orders.html" class="btn btn-sm btn-secondary"><i class="fa-regular fa-file-lines"></i> Order Receipt</a>
                        <a href="/token.html" class="btn btn-sm btn-primary"><i class="fa-solid fa-expand"></i> Fullscreen View</a>
                    </div>
                </div>
            </div>
        `;

        if (window.QRGenerator) {
            QRGenerator.renderToElement('token-qr-slot', qrPayload, 140);
        }
    }

    static playReadySound() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.type = 'sine';
            osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
            osc.frequency.setValueAtTime(880.00, ctx.currentTime + 0.15); // A5
            gain.gain.setValueAtTime(0.3, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.6);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 0.6);
        } catch (e) {
            // Audio context not allowed until interaction
        }
    }
}

window.TokenTracker = TokenTracker;
