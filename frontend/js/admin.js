/**
 * Digital Canteen Token System - Admin Controllers & Chart.js Visualizers
 */

const AdminController = {
    revenueChartInstance: null,
    peakHoursChartInstance: null,
    demandVsActualChartInstance: null,

    initOverview: async function() {
        try {
            const stats = await ApiClient.get(CONFIG.ENDPOINTS.ADMIN.DASHBOARD_STATS);
            
            document.getElementById('stat-revenue').textContent = `₹${stats.today_revenue.toFixed(2)}`;
            document.getElementById('stat-orders').textContent = stats.total_orders_today;
            document.getElementById('stat-queue').textContent = stats.active_queue_count;
            document.getElementById('stat-lowstock').textContent = stats.low_stock_count;

            this.renderRevenueChart(stats.revenue_trends);
            this.renderPeakHoursChart(stats.peak_hours);
            this.renderTopItems(stats.top_selling_items);
        } catch (e) {
            console.error('Failed to load admin stats:', e);
        }
    },

    renderRevenueChart: function(trends) {
        const ctx = document.getElementById('revenue-chart-canvas');
        if (!ctx || !trends || typeof Chart === 'undefined') return;

        if (this.revenueChartInstance) {
            this.revenueChartInstance.destroy();
        }

        this.revenueChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: trends.labels,
                datasets: [{
                    label: 'Daily Revenue (₹)',
                    data: trends.data,
                    borderColor: '#b026ff',
                    backgroundColor: 'rgba(176, 38, 255, 0.15)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: '#ff2ee6',
                    pointBorderColor: '#ffffff',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { grid: { color: 'rgba(176, 38, 255, 0.1)' }, ticks: { color: '#b3a7d4' } },
                    y: { grid: { color: 'rgba(176, 38, 255, 0.1)' }, ticks: { color: '#b3a7d4' } }
                }
            }
        });
    },

    renderPeakHoursChart: function(peakData) {
        const ctx = document.getElementById('peak-hours-chart-canvas');
        if (!ctx || !peakData || typeof Chart === 'undefined') return;

        if (this.peakHoursChartInstance) {
            this.peakHoursChartInstance.destroy();
        }

        this.peakHoursChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: peakData.map(p => p.hour),
                datasets: [{
                    label: 'Orders Volume',
                    data: peakData.map(p => p.orders),
                    backgroundColor: 'rgba(0, 229, 255, 0.65)',
                    borderColor: '#00e5ff',
                    borderWidth: 1.5,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#b3a7d4' } },
                    y: { grid: { color: 'rgba(0, 229, 255, 0.1)' }, ticks: { color: '#b3a7d4' } }
                }
            }
        });
    },

    renderTopItems: function(topItems) {
        const tbody = document.getElementById('top-items-tbody');
        if (!tbody) return;
        if (!topItems || topItems.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; color:var(--text-muted); padding:1rem;">No sales records today.</td></tr>`;
            return;
        }
        tbody.innerHTML = topItems.map((item, idx) => `
            <tr>
                <td><strong>#${idx + 1} ${item.name}</strong></td>
                <td><span class="badge badge-accent">${item.quantity_sold} portions</span></td>
                <td><strong>₹${item.revenue.toFixed(2)}</strong></td>
            </tr>
        `).join('');
    },

    loadKitchenLanes: async function(selectedCounter = 'all') {
        try {
            const tokens = await ApiClient.get(CONFIG.ENDPOINTS.TOKENS.LIVE_BOARD);
            
            const filteredTokens = selectedCounter === 'all' 
                ? tokens 
                : tokens.filter(t => t.counter_number === parseInt(selectedCounter, 10));

            const waiting = filteredTokens.filter(t => t.status === 'Waiting');
            const preparing = filteredTokens.filter(t => t.status === 'Preparing');
            const ready = filteredTokens.filter(t => t.status === 'Ready');

            document.getElementById('count-waiting').textContent = waiting.length;
            document.getElementById('count-preparing').textContent = preparing.length;
            document.getElementById('count-ready').textContent = ready.length;

            this.renderLane('lane-waiting', waiting, 'Start Prep 🍳', 'Preparing');
            this.renderLane('lane-preparing', preparing, 'Mark Ready 🔔', 'Ready');
            this.renderLane('lane-ready', ready, 'Complete & Serve ✨', 'Completed');
        } catch (e) {
            console.error('Failed to load kitchen queue:', e);
        }
    },

    renderLane: function(laneId, tokens, actionText, nextStatus) {
        const lane = document.getElementById(laneId);
        if (!lane) return;

        if (tokens.length === 0) {
            lane.innerHTML = `<div style="text-align:center; color:var(--text-muted); padding:3rem 1rem; font-size:0.85rem;">No orders in this station.</div>`;
            return;
        }

        lane.innerHTML = tokens.map(t => `
            <div class="kanban-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                    <span style="font-family:var(--font-display); font-weight:800; font-size:1.2rem; color:var(--primary);">${t.token_number}</span>
                    <span class="badge badge-${t.status.toLowerCase()}">Counter ${t.counter_number || 1}</span>
                </div>
                <div style="font-size:0.875rem; font-weight:600; color:var(--text-primary); margin-bottom:0.25rem;">${t.user_name} (${t.order_number})</div>
                <div style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:0.75rem; background:var(--bg-surface-elevated); padding:0.4rem 0.6rem; border-radius:var(--radius-sm);">
                    ${t.items_summary || 'Standard Meal'}
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.75rem; color:var(--text-muted);">Wait: ~${t.estimated_wait_minutes}m</span>
                    <button class="btn btn-sm btn-primary" onclick="AdminController.advanceTokenStatus(${t.id}, '${nextStatus}')">
                        ${actionText}
                    </button>
                </div>
            </div>
        `).join('');
    },

    advanceTokenStatus: async function(tokenId, newStatus) {
        try {
            await ApiClient.put(CONFIG.ENDPOINTS.TOKENS.UPDATE_STATUS(tokenId), { status: newStatus });
            Toast.success(`Token advanced to ${newStatus}`);
            this.loadKitchenLanes();
        } catch (err) {
            Toast.error(err.message || 'Status update failed.');
        }
    },

    loadInventoryView: async function() {
        try {
            const inventory = await ApiClient.get(CONFIG.ENDPOINTS.INVENTORY.LIST);
            const tbody = document.getElementById('inventory-table-body');
            if (!tbody) return;

            tbody.innerHTML = inventory.map(item => {
                const isLow = item.current_stock <= item.minimum_stock_alert;
                return `
                    <tr style="${isLow ? 'background:rgba(255,0,85,0.08);' : ''}">
                        <td><strong>${item.food_item ? item.food_item.name : 'Item #' + item.food_item_id}</strong></td>
                        <td><span class="badge badge-info">${item.food_item && item.food_item.category ? item.food_item.category.name : 'Category'}</span></td>
                        <td>
                            <strong style="color:${isLow ? 'var(--danger)' : 'var(--accent)'}; font-size:1.05rem;">
                                ${item.current_stock} ${item.unit}
                            </strong>
                            ${isLow ? '<span class="badge badge-cancelled" style="margin-left:0.5rem;">LOW STOCK</span>' : ''}
                        </td>
                        <td>${item.minimum_stock_alert} ${item.unit}</td>
                        <td>${new Date(item.last_restocked_at).toLocaleDateString()}</td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="AdminController.openRestockModal(${item.food_item_id}, '${item.food_item ? item.food_item.name : 'Dish'}')">
                                Restock 📦
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
        } catch (e) {
            Toast.error('Failed to load inventory.');
        }
    },

    openRestockModal: function(foodItemId, foodName) {
        document.getElementById('restock-item-id').value = foodItemId;
        document.getElementById('restock-item-name').textContent = foodName;
        document.getElementById('restock-modal').classList.add('open');
    },

    closeRestockModal: function() {
        document.getElementById('restock-modal').classList.remove('open');
    },

    submitRestock: async function(event) {
        event.preventDefault();
        const foodId = document.getElementById('restock-item-id').value;
        const addQty = parseInt(document.getElementById('restock-quantity').value, 10);
        const reason = document.getElementById('restock-reason').value;

        try {
            await ApiClient.put(CONFIG.ENDPOINTS.INVENTORY.RESTOCK(foodId), { add_quantity: addQty, reason });
            Toast.success('Stock updated successfully!');
            this.closeRestockModal();
            this.loadInventoryView();
        } catch (err) {
            Toast.error(err.message || 'Restock failed.');
        }
    },

    loadAIAnalytics: async function() {
        try {
            const queue = await ApiClient.get(CONFIG.ENDPOINTS.AI.QUEUE_STATUS);
            document.getElementById('ai-crowd-level').textContent = queue.crowd_level;
            document.getElementById('ai-avg-wait').textContent = `~${queue.estimated_average_wait_minutes} mins`;

            const forecast = await ApiClient.post(CONFIG.ENDPOINTS.AI.DEMAND_FORECAST, { meal_slot: 'Lunch' });
            document.getElementById('ai-total-forecast').textContent = `${forecast.total_predicted_items} dishes`;
            document.getElementById('ai-total-prep').textContent = `${forecast.total_prep_units} portions`;

            this.renderForecastTable(forecast.items);
            this.loadDemandVsActualChart();
        } catch (e) {
            console.error('Failed to load AI analytics:', e);
        }
    },

    renderForecastTable: function(items) {
        const tbody = document.getElementById('forecast-table-body');
        if (!tbody) return;

        tbody.innerHTML = items.map(item => `
            <tr>
                <td><strong>${item.name}</strong></td>
                <td><span class="badge badge-info">${item.meal_slot}</span></td>
                <td><strong style="color:var(--text-primary); font-size:1rem;">${item.predicted_demand} units</strong></td>
                <td>
                    <strong style="color:var(--accent); font-size:1.05rem;">${item.recommended_prep_quantity} units</strong>
                    ${item.has_admin_override ? '<span class="badge badge-accent" style="margin-left:0.5rem;">MANUAL OVERRIDE</span>' : ''}
                </td>
                <td>${item.lower_bound} - ${item.upper_bound} units</td>
                <td>
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span class="badge badge-success">${(item.confidence_score * 100).toFixed(0)}%</span>
                        <button class="btn btn-sm btn-outline" onclick="AdminController.openOverrideModal(${item.food_item_id}, '${item.name}', ${item.predicted_demand}, '${item.meal_slot}')">
                            Override ✏️
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    },

    loadDemandVsActualChart: async function() {
        try {
            const data = await ApiClient.get(CONFIG.ENDPOINTS.AI.DEMAND_VS_ACTUAL, { days: 7 });
            const ctx = document.getElementById('demand-vs-actual-canvas');
            if (!ctx || typeof Chart === 'undefined') return;

            // Group by date
            const dates = [...new Set(data.data.map(d => d.date))];
            const predictedByDate = dates.map(dt => {
                const pts = data.data.filter(d => d.date === dt);
                return pts.reduce((sum, p) => sum + p.predicted_demand, 0);
            });
            const actualByDate = dates.map(dt => {
                const pts = data.data.filter(d => d.date === dt);
                return pts.reduce((sum, p) => sum + p.actual_demand, 0);
            });

            if (this.demandVsActualChartInstance) {
                this.demandVsActualChartInstance.destroy();
            }

            this.demandVsActualChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: dates,
                    datasets: [
                        {
                            label: 'AI Predicted Demand',
                            data: predictedByDate,
                            backgroundColor: 'rgba(176, 38, 255, 0.7)',
                            borderColor: '#b026ff',
                            borderWidth: 1
                        },
                        {
                            label: 'Actual Recorded Sales',
                            data: actualByDate,
                            backgroundColor: 'rgba(0, 229, 255, 0.7)',
                            borderColor: '#00e5ff',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { color: 'rgba(176, 38, 255, 0.1)' }, ticks: { color: '#b3a7d4' } },
                        y: { grid: { color: 'rgba(176, 38, 255, 0.1)' }, ticks: { color: '#b3a7d4' } }
                    }
                }
            });
        } catch (e) {
            console.error('Failed to load demand vs actual chart:', e);
        }
    },

    openOverrideModal: function(foodId, foodName, currentPred, mealSlot) {
        document.getElementById('override-food-id').value = foodId;
        document.getElementById('override-food-name').textContent = foodName;
        document.getElementById('override-pred-display').textContent = `${currentPred} units`;
        document.getElementById('override-quantity').value = currentPred + 10;
        document.getElementById('override-slot').value = mealSlot;
        document.getElementById('override-modal').classList.add('open');
    },

    closeOverrideModal: function() {
        document.getElementById('override-modal').classList.remove('open');
    },

    submitOverride: async function(event) {
        event.preventDefault();
        const foodId = parseInt(document.getElementById('override-food-id').value, 10);
        const overrideQty = parseInt(document.getElementById('override-quantity').value, 10);
        const mealSlot = document.getElementById('override-slot').value;
        const reason = document.getElementById('override-reason').value;
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);

        try {
            await ApiClient.post(CONFIG.ENDPOINTS.AI.DEMAND_OVERRIDE, {
                food_item_id: foodId,
                prediction_date: tomorrow.toISOString().split('T')[0],
                meal_slot: mealSlot,
                override_quantity: overrideQty,
                reason: reason
            });
            Toast.success('Prediction override logged!');
            this.closeOverrideModal();
            this.loadAIAnalytics();
        } catch (err) {
            Toast.error(err.message || 'Override failed.');
        }
    },

    exportSalesReport: async function() {
        try {
            Toast.info('Preparing sales report CSV download...');
            const blob = await ApiClient.get(CONFIG.ENDPOINTS.ADMIN.EXPORT_SALES, { format: 'csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `canteen_sales_report_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            Toast.success('Sales report downloaded!');
        } catch (err) {
            Toast.error(err.message || 'Report download failed.');
        }
    }
};

window.AdminController = AdminController;
