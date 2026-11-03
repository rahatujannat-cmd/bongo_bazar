/**
 * BongoBazaar - Main Client Script
 * Cart, Wishlist, Search, Notifications, Language, and Utility Functions
 */

// Cart State Management
const Cart = {
    key: 'bongobazaar_cart_v1',
    items: [],

    init() {
        try {
            const saved = localStorage.getItem(this.key);
            this.items = saved ? JSON.parse(saved) : [];
        } catch (e) {
            this.items = [];
        }
        this.updateBadge();
        this.renderDrawer();
    },

    save() {
        try {
            localStorage.setItem(this.key, JSON.stringify(this.items));
        } catch (e) {
            console.error('Error saving cart', e);
        }
        this.updateBadge();
        this.renderDrawer();
        window.dispatchEvent(new CustomEvent('cart-updated', { detail: { items: this.items } }));
    },

    addItem(product, quantity = 1, color = null, size = null) {
        quantity = parseInt(quantity) || 1;
        const colorVal = color || (product.colors_list && product.colors_list.length > 0 ? product.colors_list[0] : '');
        const sizeVal = size || (product.sizes_list && product.sizes_list.length > 0 ? product.sizes_list[0] : '');
        const unitPrice = (product.sale_price && product.sale_price > 0) ? product.sale_price : product.price;

        // Check if item already exists with matching color & size
        const existingIndex = this.items.findIndex(i => 
            i.id === product.id && i.color === colorVal && i.size === sizeVal
        );

        if (existingIndex > -1) {
            this.items[existingIndex].quantity += quantity;
        } else {
            this.items.push({
                id: product.id,
                title: product.title,
                title_bn: product.title_bn || product.title,
                price: parseFloat(unitPrice),
                regular_price: parseFloat(product.price),
                quantity: quantity,
                color: colorVal,
                size: sizeVal,
                image: product.image,
                stock: product.stock || 99
            });
        }

        this.save();
        showToast('কার্টে যুক্ত হয়েছে!', `${product.title} আপনার কার্টে যোগ করা হয়েছে।`, 'success');
        openCartDrawer();
    },

    updateQuantity(index, delta) {
        if (!this.items[index]) return;
        this.items[index].quantity += delta;
        if (this.items[index].quantity <= 0) {
            this.removeItem(index);
            return;
        }
        if (this.items[index].stock && this.items[index].quantity > this.items[index].stock) {
            this.items[index].quantity = this.items[index].stock;
            showToast('স্টক শেষ!', `সর্বোচ্চ প্রাপ্তব্য পরিমাণ ${this.items[index].stock} টি`, 'warning');
        }
        this.save();
    },

    removeItem(index) {
        if (this.items[index]) {
            const removed = this.items.splice(index, 1);
            this.save();
            showToast('পণ্য সরানো হয়েছে', 'কার্ট থেকে পণ্য সরানো হয়েছে', 'info');
        }
    },

    clear() {
        this.items = [];
        this.save();
    },

    getCount() {
        return this.items.reduce((sum, item) => sum + item.quantity, 0);
    },

    getSubtotal() {
        return this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    },

    updateBadge() {
        const count = this.getCount();
        document.querySelectorAll('.cart-badge-count').forEach(el => {
            el.textContent = count;
            el.classList.toggle('hidden', count === 0);
        });
    },

    renderDrawer() {
        const container = document.getElementById('cart-drawer-items');
        const emptyState = document.getElementById('cart-drawer-empty');
        const subtotalEl = document.getElementById('cart-drawer-subtotal');
        const footerEl = document.getElementById('cart-drawer-footer');

        if (!container) return;

        if (this.items.length === 0) {
            container.innerHTML = '';
            if (emptyState) emptyState.classList.remove('hidden');
            if (footerEl) footerEl.classList.add('hidden');
            return;
        }

        if (emptyState) emptyState.classList.add('hidden');
        if (footerEl) footerEl.classList.remove('hidden');

        let html = '';
        this.items.forEach((item, index) => {
            html += `
            <div class="flex items-center gap-3 py-3 border-b border-slate-100 last:border-b-0">
                <img src="${item.image}" alt="${item.title}" class="w-16 h-16 object-cover rounded-lg border border-slate-200">
                <div class="flex-1 min-w-0">
                    <h4 class="text-sm font-semibold text-slate-800 truncate">${item.title}</h4>
                    <div class="flex items-center gap-2 text-xs text-slate-500 mt-0.5">
                        ${item.color ? `<span>রঙ: ${item.color}</span>` : ''}
                        ${item.size ? `<span>সাইজ: ${item.size}</span>` : ''}
                    </div>
                    <div class="flex items-center justify-between mt-2">
                        <span class="text-sm font-bold text-sky-600">৳${(item.price * item.quantity).toLocaleString('en-IN')}</span>
                        <div class="flex items-center border border-slate-200 rounded-md bg-white">
                            <button onclick="Cart.updateQuantity(${index}, -1)" class="w-6 h-6 flex items-center justify-center text-slate-600 hover:bg-slate-100 rounded-l text-sm font-bold">-</button>
                            <span class="w-7 text-center text-xs font-semibold">${item.quantity}</span>
                            <button onclick="Cart.updateQuantity(${index}, 1)" class="w-6 h-6 flex items-center justify-center text-slate-600 hover:bg-slate-100 rounded-r text-sm font-bold">+</button>
                        </div>
                    </div>
                </div>
                <button onclick="Cart.removeItem(${index})" class="text-slate-400 hover:text-red-500 p-1">
                    <i data-lucide="trash-2" class="w-4 h-4"></i>
                </button>
            </div>
            `;
        });

        container.innerHTML = html;
        if (subtotalEl) {
            subtotalEl.textContent = `৳${this.getSubtotal().toLocaleString('en-IN')}`;
        }
        if (window.lucide) lucide.createIcons();
    }
};

// Wishlist State Management
const Wishlist = {
    key: 'bongobazaar_wishlist_v1',
    items: [],

    init() {
        try {
            const saved = localStorage.getItem(this.key);
            this.items = saved ? JSON.parse(saved) : [];
        } catch (e) {
            this.items = [];
        }
        this.updateBadge();
        this.updateHearts();
    },

    save() {
        try {
            localStorage.setItem(this.key, JSON.stringify(this.items));
        } catch (e) {
            console.error('Error saving wishlist', e);
        }
        this.updateBadge();
        this.updateHearts();
        window.dispatchEvent(new CustomEvent('wishlist-updated', { detail: { items: this.items } }));
    },

    toggle(product) {
        const index = this.items.findIndex(i => i.id === product.id);
        if (index > -1) {
            this.items.splice(index, 1);
            showToast('উইশলিস্ট থেকে সরানো হয়েছে', `${product.title} সরানো হয়েছে`, 'info');
        } else {
            this.items.push(product);
            showToast('উইশলিস্টে যুক্ত হয়েছে!', `${product.title} উইশলিস্টে সেভ করা হলো`, 'success');
        }
        this.save();
    },

    has(productId) {
        return this.items.some(i => i.id === productId);
    },

    updateBadge() {
        const count = this.items.length;
        document.querySelectorAll('.wishlist-badge-count').forEach(el => {
            el.textContent = count;
            el.classList.toggle('hidden', count === 0);
        });
    },

    updateHearts() {
        document.querySelectorAll('[data-wishlist-id]').forEach(btn => {
            const id = parseInt(btn.getAttribute('data-wishlist-id'));
            const heartIcon = btn.querySelector('svg, i');
            if (this.has(id)) {
                btn.classList.add('text-red-500');
                if (heartIcon) heartIcon.style.fill = '#ef4444';
            } else {
                btn.classList.remove('text-red-500');
                if (heartIcon) heartIcon.style.fill = 'none';
            }
        });
    }
};

// Cart Drawer open/close
function openCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-drawer-overlay');
    if (drawer && overlay) {
        overlay.classList.remove('hidden');
        drawer.classList.remove('translate-x-full');
        document.body.classList.add('overflow-hidden');
    }
}

function closeCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-drawer-overlay');
    if (drawer && overlay) {
        drawer.classList.add('translate-x-full');
        overlay.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    }
}

// Toast Notifications
function showToast(title, message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none px-4 sm:px-0';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `pointer-events-auto flex items-start gap-3 p-4 rounded-xl shadow-xl border bg-white transform transition-all duration-300 translate-y-4 opacity-0`;

    let iconHtml = '';
    let borderClass = 'border-slate-200';
    if (type === 'success') {
        borderClass = 'border-emerald-300 border-l-4 border-l-emerald-500';
        iconHtml = `<div class="p-1 rounded-full bg-emerald-100 text-emerald-600"><i data-lucide="check" class="w-4 h-4"></i></div>`;
    } else if (type === 'warning') {
        borderClass = 'border-amber-300 border-l-4 border-l-amber-500';
        iconHtml = `<div class="p-1 rounded-full bg-amber-100 text-amber-600"><i data-lucide="alert-triangle" class="w-4 h-4"></i></div>`;
    } else if (type === 'error') {
        borderClass = 'border-red-300 border-l-4 border-l-red-500';
        iconHtml = `<div class="p-1 rounded-full bg-red-100 text-red-600"><i data-lucide="alert-circle" class="w-4 h-4"></i></div>`;
    } else {
        borderClass = 'border-sky-300 border-l-4 border-l-sky-500';
        iconHtml = `<div class="p-1 rounded-full bg-sky-100 text-sky-600"><i data-lucide="info" class="w-4 h-4"></i></div>`;
    }

    toast.className += ` ${borderClass}`;
    toast.innerHTML = `
        ${iconHtml}
        <div class="flex-1 min-w-0">
            <h5 class="text-sm font-semibold text-slate-800">${title}</h5>
            <p class="text-xs text-slate-600 mt-0.5">${message}</p>
        </div>
        <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-slate-600">
            <i data-lucide="x" class="w-4 h-4"></i>
        </button>
    `;

    container.appendChild(toast);
    if (window.lucide) lucide.createIcons();

    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-y-4', 'opacity-0');
    }, 10);

    // Auto remove after 3.5 seconds
    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Currency Formatter
function formatBDT(amount) {
    return '৳' + parseFloat(amount || 0).toLocaleString('en-IN');
}

// Live Search Autocomplete
function initSearchAutocomplete() {
    const searchInputs = document.querySelectorAll('.live-search-input');
    searchInputs.forEach(input => {
        const resultsContainer = input.parentElement.querySelector('.search-results-dropdown');
        if (!resultsContainer) return;

        let debounceTimer;
        input.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            clearTimeout(debounceTimer);

            if (query.length < 2) {
                resultsContainer.classList.add('hidden');
                resultsContainer.innerHTML = '';
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`/api/products?search=${encodeURIComponent(query)}&limit=6`)
                    .then(res => res.json())
                    .then(data => {
                        if (!data.products || data.products.length === 0) {
                            resultsContainer.innerHTML = `
                                <div class="p-4 text-center text-sm text-slate-500">
                                    কোনো পণ্য পাওয়া যায়নি
                                </div>
                            `;
                            resultsContainer.classList.remove('hidden');
                            return;
                        }

                        let html = '<div class="divide-y divide-slate-100 max-h-80 overflow-y-auto">';
                        data.products.forEach(p => {
                            const pPrice = p.sale_price ? p.sale_price : p.price;
                            html += `
                            <a href="/product/${p.id}" class="flex items-center gap-3 p-3 hover:bg-slate-50 transition-colors">
                                <img src="${p.image}" alt="${p.title}" class="w-12 h-12 object-cover rounded-md border">
                                <div class="flex-1 min-w-0">
                                    <p class="text-sm font-medium text-slate-800 truncate">${p.title}</p>
                                    <p class="text-xs text-slate-500">${p.category_name} &bull; ${p.brand || 'BongoBazaar'}</p>
                                    <div class="flex items-center gap-2 mt-0.5">
                                        <span class="text-xs font-bold text-sky-600">৳${pPrice.toLocaleString('en-IN')}</span>
                                        ${p.sale_price ? `<span class="text-xs text-slate-400 line-through">৳${p.price.toLocaleString('en-IN')}</span>` : ''}
                                    </div>
                                </div>
                            </a>
                            `;
                        });
                        html += `
                            <div class="p-2 bg-slate-50 text-center border-t border-slate-100">
                                <a href="/shop?search=${encodeURIComponent(query)}" class="text-xs font-semibold text-sky-600 hover:underline">সকল ${data.count} টি ফলাফল দেখুন &rarr;</a>
                            </div>
                        </div>`;

                        resultsContainer.innerHTML = html;
                        resultsContainer.classList.remove('hidden');
                    })
                    .catch(() => {
                        resultsContainer.classList.add('hidden');
                    });
            }, 300);
        });

        // Close on click outside
        document.addEventListener('click', (e) => {
            if (!input.contains(e.target) && !resultsContainer.contains(e.target)) {
                resultsContainer.classList.add('hidden');
            }
        });
    });
}

// Flash Sale Countdown Timer
function initFlashSaleTimer() {
    const timerContainer = document.getElementById('flash-sale-timer');
    if (!timerContainer) return;

    // End time is end of today
    const now = new Date();
    const endOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59).getTime();

    function update() {
        const currentTime = new Date().getTime();
        const diff = Math.max(0, endOfDay - currentTime);

        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);

        const hEl = document.getElementById('flash-hours');
        const mEl = document.getElementById('flash-minutes');
        const sEl = document.getElementById('flash-seconds');

        if (hEl) hEl.textContent = String(hours).padStart(2, '0');
        if (mEl) mEl.textContent = String(minutes).padStart(2, '0');
        if (sEl) sEl.textContent = String(seconds).padStart(2, '0');
    }

    update();
    setInterval(update, 1000);
}

// Demo Login Helper
function loginAsDemo(role = 'customer') {
    fetch('/api/auth/demo-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: role })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast('স্বাগতম!', data.message, 'success');
            setTimeout(() => {
                if (role === 'admin') {
                    window.location.href = '/admin';
                } else {
                    window.location.href = '/account';
                }
            }, 600);
        } else {
            showToast('লগইন ব্যর্থ', data.message, 'error');
        }
    });
}

// Logout Helper
function logoutUser() {
    fetch('/api/auth/logout', { method: 'POST' })
        .then(res => res.json())
        .then(() => {
            showToast('লগআউট সম্পন্ন', 'আপনি সফলভাবে লগআউট হয়েছেন', 'info');
            setTimeout(() => {
                window.location.href = '/';
            }, 600);
        });
}

// Quick Buy
function quickBuy(product, qty = 1, color = null, size = null) {
    Cart.addItem(product, qty, color, size);
    window.location.href = '/checkout';
}

// DOM Ready initialization
document.addEventListener('DOMContentLoaded', () => {
    Cart.init();
    Wishlist.init();
    initSearchAutocomplete();
    initFlashSaleTimer();

    if (window.lucide) {
        lucide.createIcons();
    }
});
