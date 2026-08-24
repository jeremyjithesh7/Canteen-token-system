/**
 * Digital Canteen Token System - Cart & Checkout Manager
 */

class Cart {
    static init() {
        this.updateBadge();
        this.renderDrawer();
        this.updateSteppers();
    }

    static getItems() {
        try {
            const raw = localStorage.getItem('canteen_cart_items');
            return raw ? JSON.parse(raw) : [];
        } catch (e) {
            return [];
        }
    }

    static saveItems(items) {
        localStorage.setItem('canteen_cart_items', JSON.stringify(items));
        this.updateBadge();
        this.renderDrawer();
        this.updateSteppers();
    }

    static getItemQuantity(foodItemId) {
        const items = this.getItems();
        const found = items.find(i => (i.id === foodItemId || i.food_item_id === foodItemId));
        return found ? found.quantity : 0;
    }

    static addItem(foodItem, quantity = 1) {
        let items = this.getItems();
        const fid = foodItem.id || foodItem.food_item_id;
        const index = items.findIndex(i => (i.id === fid || i.food_item_id === fid));
        if (index > -1) {
            items[index].quantity += quantity;
        } else {
            items.push({
                id: fid,
                food_item_id: fid,
                name: foodItem.name,
                price: parseFloat(foodItem.price),
                image_url: foodItem.image_url,
                counter_id: foodItem.counter_id || 1,
                category_name: foodItem.category ? foodItem.category.name : 'South Indian',
                is_veg: foodItem.is_veg !== undefined ? foodItem.is_veg : true,
                prep_time_minutes: foodItem.prep_time_minutes || 10,
                quantity: quantity
            });
        }
        this.saveItems(items);
    }

    static updateQuantity(foodItemId, delta, itemData = null) {
        let items = this.getItems();
        const index = items.findIndex(i => (i.id === foodItemId || i.food_item_id === foodItemId));

        if (index > -1) {
            items[index].quantity += delta;
            if (items[index].quantity <= 0) {
                items.splice(index, 1);
            }
        } else if (delta > 0 && itemData) {
            try {
                let item = itemData;
                if (typeof itemData === 'string') {
                    item = JSON.parse(unescape(itemData));
                }
                items.push({
                    id: item.id,
                    name: item.name,
                    price: parseFloat(item.price),
                    image_url: item.image_url,
                    counter_id: item.counter_id || 1,
                    category_name: item.category ? item.category.name : 'Stall',
                    is_veg: item.is_veg,
                    prep_time_minutes: item.prep_time_minutes,
                    quantity: delta
                });
            } catch (e) {
                console.error("Failed to add food item to cart:", e);
            }
        }

        this.saveItems(items);
    }

    static updateSteppers() {
        const items = this.getItems();
        document.querySelectorAll('.stepper-val').forEach(el => {
            const id = parseInt(el.id.replace('qty-val-', ''), 10);
            if (!isNaN(id)) {
                const found = items.find(i => i.id === id);
                el.textContent = found ? found.quantity : 0;
            }
        });
    }

    static removeItem(foodItemId) {
        let items = this.getItems();
        items = items.filter(i => i.id !== foodItemId);
        this.saveItems(items);
    }

    static clear() {
        localStorage.removeItem('canteen_cart_items');
        this.updateBadge();
        this.renderDrawer();
        this.updateSteppers();
    }

    static getTotalCount() {
        return this.getItems().reduce((sum, item) => sum + item.quantity, 0);
    }

    static getTotalAmount() {
        return this.getItems().reduce((sum, item) => sum + (item.price * item.quantity), 0);
    }

    static updateBadge() {
        const count = this.getTotalCount();
        const badge = document.getElementById('cart-count-badge');
        if (badge) {
            badge.textContent = count;
        }
        document.querySelectorAll('.cart-badge-count').forEach(b => {
            b.textContent = count;
            b.style.display = count > 0 ? 'inline-flex' : 'none';
        });
    }

    static toggleDrawer() {
        const drawer = document.getElementById('cart-drawer');
        if (drawer) {
            drawer.classList.toggle('open');
            this.renderDrawer();
        }
    }

    static openDrawer() {
        const drawer = document.getElementById('cart-drawer');
        if (drawer) {
            drawer.classList.add('open');
            this.renderDrawer();
        }
    }

    static closeDrawer() {
        const drawer = document.getElementById('cart-drawer');
        if (drawer) {
            drawer.classList.remove('open');
        }
    }

    static renderDrawer() {
        const listContainer = document.getElementById('cart-items-list');
        const totalAmountSlot = document.getElementById('cart-total-amount');
        if (!listContainer) return;

        const items = this.getItems();
        if (totalAmountSlot) {
            totalAmountSlot.textContent = `₹${this.getTotalAmount().toFixed(2)}`;
        }

        if (items.length === 0) {
            listContainer.innerHTML = `
                <div class="empty-state" style="padding:2rem 1rem;">
                    <div class="empty-state-icon">🛒</div>
                    <h4 style="font-size:1.1rem; margin-bottom:0.25rem;">Cart is Empty</h4>
                    <p style="font-size:0.85rem; color:var(--text-secondary);">Add delicious dishes from the menu above to start your order.</p>
                </div>
            `;
            return;
        }

        listContainer.innerHTML = items.map(item => `
            <div style="display:flex; justify-content:space-between; align-items:center; background:var(--bg-surface-elevated); padding:0.9rem; border-radius:var(--radius-md); border:1px solid var(--border);">
                <div style="flex:1;">
                    <div style="font-weight:700; font-size:0.95rem;">${item.name}</div>
                    <div style="font-size:0.8rem; color:var(--text-muted); margin-top:0.15rem;">
                        ₹${item.price.toFixed(2)} each • Counter ${item.counter_id || 1}
                    </div>
                </div>

                <div style="display:flex; align-items:center; gap:0.75rem;">
                    <div class="quantity-stepper">
                        <button class="stepper-btn" onclick="Cart.updateQuantity(${item.id}, -1)">-</button>
                        <span class="stepper-val">${item.quantity}</span>
                        <button class="stepper-btn" onclick="Cart.updateQuantity(${item.id}, 1)">+</button>
                    </div>
                    <button class="btn btn-sm btn-icon btn-outline" style="color:var(--danger);" onclick="Cart.removeItem(${item.id})" title="Remove">✕</button>
                </div>
            </div>
        `).join('');
    }

    static async proceedToCheckout() {
        if (!Auth.isAuthenticated()) {
            Toast.info('Please sign in or create an account to place an order.');
            setTimeout(() => {
                window.location.href = '/login.html';
            }, 600);
            return;
        }

        const items = this.getItems();
        if (items.length === 0) {
            Toast.error('Please add items to your cart first.');
            return;
        }

        const btn = document.getElementById('checkout-btn');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span> Processing Order...';
        }

        const paymentMethod = document.getElementById('payment-method-select') ? document.getElementById('payment-method-select').value : 'UPI';
        const notes = document.getElementById('order-notes') ? document.getElementById('order-notes').value.trim() : '';

        const payload = {
            items: items.map(item => ({
                food_item_id: item.id,
                quantity: item.quantity
            })),
            payment_method: paymentMethod,
            notes: notes
        };

        try {
            const orderResult = await ApiClient.post(CONFIG.ENDPOINTS.ORDERS.CREATE, payload);
            this.clear();
            this.closeDrawer();
            Toast.success(`Order ${orderResult.order_number} confirmed! Generating token...`);

            setTimeout(() => {
                window.location.href = `/token.html?id=${orderResult.token ? orderResult.token.id : ''}`;
            }, 500);
        } catch (err) {
            Toast.error(err.message || 'Failed to place order. Please try again.');
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = 'Pay & Generate Digital Token ✨';
            }
        }
    }
}

window.Cart = Cart;
