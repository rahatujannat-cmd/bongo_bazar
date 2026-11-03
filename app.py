"""
BongoBazaar - Bangladesh's Complete E-Commerce Platform
Flask Backend with RESTful APIs, Session Management, SQLite Database, and Template Views.
"""
import os
import json
import sqlite3
import random
from datetime import datetime, timedelta
from functools import wraps
from flask import (
    Flask, render_template, request, jsonify, session,
    redirect, url_for, g, make_response
)
from database import get_db, hash_password, init_db, seed_db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'bongobazaar-super-secret-key-2026-bangladesh')
app.config['JSON_SORT_KEYS'] = False

# Ensure DB initialized
init_db()
seed_db()

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email, phone, role, address, city, district FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        g.user = dict(user) if user else None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user or g.user.get('role') != 'admin':
            return redirect(url_for('login_page', next=request.url, error='Admin access required'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# PAGE ROUTES
# ==========================================

@app.route('/')
def home_page():
    conn = get_db()
    c = conn.cursor()
    # Featured categories
    c.execute('SELECT * FROM categories ORDER BY id ASC')
    categories = [dict(row) for row in c.fetchall()]

    # Flash Sale Products
    c.execute('SELECT * FROM products WHERE is_flash_sale = 1 AND stock > 0 LIMIT 6')
    flash_products = [dict(row) for row in c.fetchall()]

    # Featured Products
    c.execute('SELECT * FROM products WHERE is_featured = 1 AND stock > 0 LIMIT 8')
    featured_products = [dict(row) for row in c.fetchall()]

    # Best Selling Products (or highest rating)
    c.execute('SELECT * FROM products ORDER BY review_count DESC, rating DESC LIMIT 8')
    best_sellers = [dict(row) for row in c.fetchall()]

    conn.close()
    return render_template(
        'index.html',
        categories=categories,
        flash_products=flash_products,
        featured_products=featured_products,
        best_sellers=best_sellers
    )

@app.route('/shop')
def shop_page():
    return render_template('shop.html')

@app.route('/product/<int:product_id>')
def product_detail_page(product_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return render_template('404.html', message="Product not found"), 404
    product = dict(row)

    # Parse JSON fields safely
    product['gallery_list'] = json.loads(product['gallery']) if product['gallery'] else [product['image']]
    product['colors_list'] = json.loads(product['colors']) if product['colors'] else []
    product['sizes_list'] = json.loads(product['sizes']) if product['sizes'] else []

    # Get Reviews
    c.execute('SELECT * FROM reviews WHERE product_id = ? ORDER BY created_at DESC', (product_id,))
    reviews = [dict(r) for r in c.fetchall()]

    # Related Products from same category
    c.execute('SELECT * FROM products WHERE category_id = ? AND id != ? LIMIT 4', (product['category_id'], product_id))
    related = [dict(r) for r in c.fetchall()]

    conn.close()
    return render_template('product_detail.html', product=product, reviews=reviews, related=related)

@app.route('/cart')
def cart_page():
    return render_template('cart.html')

@app.route('/checkout')
def checkout_page():
    return render_template('checkout.html')

@app.route('/order-confirmation/<order_number>')
def order_confirmation_page(order_number):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE order_number = ?', (order_number,))
    order_row = c.fetchone()
    if not order_row:
        conn.close()
        return redirect(url_for('home_page'))
    
    order = dict(order_row)
    c.execute('SELECT * FROM order_items WHERE order_id = ?', (order['id'],))
    order['items_list'] = [dict(i) for i in c.fetchall()]
    conn.close()
    return render_template('order_confirmation.html', order=order)

@app.route('/track')
def track_order_page():
    order_no = request.args.get('order_no', '')
    return render_template('track_order.html', initial_order_no=order_no)

@app.route('/wishlist')
def wishlist_page():
    return render_template('wishlist.html')

@app.route('/account')
def account_page():
    if not g.user:
        return redirect(url_for('login_page', next=url_for('account_page')))
    return render_template('account.html')

@app.route('/login')
def login_page():
    if g.user:
        if g.user.get('role') == 'admin':
            return redirect(url_for('admin_dashboard_page'))
        return redirect(url_for('account_page'))
    return render_template('auth.html', initial_tab='login')

@app.route('/register')
def register_page():
    if g.user:
        return redirect(url_for('account_page'))
    return render_template('auth.html', initial_tab='register')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

@app.route('/terms')
def terms_page():
    return render_template('terms.html')

@app.route('/returns')
def returns_page():
    return render_template('refund_policy.html')

@app.route('/privacy')
def privacy_page():
    return render_template('privacy_policy.html')

# ==========================================
# ADMIN PAGE ROUTES
# ==========================================

@app.route('/admin')
@admin_required
def admin_dashboard_page():
    return render_template('admin/dashboard.html')

@app.route('/admin/products')
@admin_required
def admin_products_page():
    return render_template('admin/products.html')

@app.route('/admin/orders')
@admin_required
def admin_orders_page():
    return render_template('admin/orders.html')

@app.route('/admin/customers')
@admin_required
def admin_customers_page():
    return render_template('admin/customers.html')

@app.route('/admin/coupons')
@admin_required
def admin_coupons_page():
    return render_template('admin/coupons.html')

@app.route('/admin/invoice/<order_number>')
def admin_invoice_page(order_number):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE order_number = ?', (order_number,))
    order_row = c.fetchone()
    if not order_row:
        conn.close()
        return "Invoice not found", 404
    order = dict(order_row)
    c.execute('SELECT * FROM order_items WHERE order_id = ?', (order['id'],))
    order['items_list'] = [dict(i) for i in c.fetchall()]
    conn.close()
    return render_template('admin/invoice.html', order=order)

# ==========================================
# REST API ENDPOINTS
# ==========================================

# --- Auth APIs ---
@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'নাম, ইমেইল এবং পাসওয়ার্ড আবশ্যক'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'message': 'পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'এই ইমেইল দিয়ে ইতোমধ্যে একটি অ্যাকাউন্ট রয়েছে'}), 400

    pw_hash = hash_password(password)
    cursor.execute('''
    INSERT INTO users (name, email, phone, password_hash, role)
    VALUES (?, ?, ?, ?, 'customer')
    ''', (name, email, phone, pw_hash))
    user_id = cursor.lastrowid
    conn.commit()

    session['user_id'] = user_id
    session['role'] = 'customer'
    conn.close()

    return jsonify({
        'success': True,
        'message': 'রেজিস্ট্রেশন সফল হয়েছে!',
        'user': {'id': user_id, 'name': name, 'email': email, 'phone': phone, 'role': 'customer'}
    })

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    identifier = data.get('identifier', '').strip() # can be email or phone
    password = data.get('password', '')

    if not identifier or not password:
        return jsonify({'success': False, 'message': 'ইমেইল/ফোন নম্বর ও পাসওয়ার্ড প্রদান করুন'}), 400

    pw_hash = hash_password(password)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, name, email, phone, role, address, city, district
    FROM users
    WHERE (email = ? OR phone = ?) AND password_hash = ?
    ''', (identifier.lower(), identifier, pw_hash))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({'success': False, 'message': 'ভুল ইমেইল/ফোন অথবা পাসওয়ার্ড'}), 401

    session['user_id'] = user['id']
    session['role'] = user['role']

    return jsonify({
        'success': True,
        'message': 'লগইন সফল হয়েছে!',
        'user': dict(user)
    })

@app.route('/api/auth/demo-login', methods=['POST'])
def api_demo_login():
    data = request.get_json() or {}
    role = data.get('role', 'customer') # 'admin' or 'customer'

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, phone, role, address, city, district FROM users WHERE role = ? LIMIT 1', (role,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({'success': False, 'message': 'Demo account not found'}), 404

    session['user_id'] = user['id']
    session['role'] = user['role']

    return jsonify({
        'success': True,
        'message': f'লগইন সফল ({role.capitalize()})!',
        'user': dict(user)
    })

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True, 'message': 'সফলভাবে লগআউট হয়েছেন'})

@app.route('/api/auth/me')
def api_me():
    if not g.user:
        return jsonify({'authenticated': False, 'user': None})
    return jsonify({'authenticated': True, 'user': g.user})

@app.route('/api/auth/profile', methods=['PUT'])
def api_update_profile():
    if not g.user:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.get_json() or {}
    name = data.get('name', g.user['name']).strip()
    phone = data.get('phone', g.user['phone']).strip()
    address = data.get('address', '').strip()
    city = data.get('city', '').strip()
    district = data.get('district', '').strip()

    conn = get_db()
    c = conn.cursor()
    c.execute('''
    UPDATE users SET name = ?, phone = ?, address = ?, city = ?, district = ?
    WHERE id = ?
    ''', (name, phone, address, city, district, g.user['id']))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'প্রোফাইল সফলভাবে আপডেট করা হয়েছে'})

# --- Products & Catalog APIs ---
@app.route('/api/products')
def api_get_products():
    conn = get_db()
    c = conn.cursor()

    query = 'SELECT * FROM products WHERE 1=1'
    params = []

    search = request.args.get('search', '').strip()
    if search:
        query += ' AND (title LIKE ? OR title_bn LIKE ? OR brand LIKE ? OR description LIKE ?)'
        wildcard = f'%{search}%'
        params.extend([wildcard, wildcard, wildcard, wildcard])

    category = request.args.get('category', '').strip()
    if category and category != 'all':
        query += ' AND (category_id = ? OR category_name LIKE ?)'
        params.extend([category, f'%{category}%'])

    brand = request.args.get('brand', '').strip()
    if brand and brand != 'all':
        query += ' AND brand = ?'
        params.append(brand)

    min_price = request.args.get('min_price', type=float)
    if min_price is not None:
        query += ' AND (CASE WHEN sale_price IS NOT NULL AND sale_price > 0 THEN sale_price ELSE price END) >= ?'
        params.append(min_price)

    max_price = request.args.get('max_price', type=float)
    if max_price is not None:
        query += ' AND (CASE WHEN sale_price IS NOT NULL AND sale_price > 0 THEN sale_price ELSE price END) <= ?'
        params.append(max_price)

    in_stock = request.args.get('in_stock', type=int)
    if in_stock == 1:
        query += ' AND stock > 0'

    featured = request.args.get('featured', type=int)
    if featured == 1:
        query += ' AND is_featured = 1'

    flash = request.args.get('flash', type=int)
    if flash == 1:
        query += ' AND is_flash_sale = 1'

    # Sorting
    sort = request.args.get('sort', 'default')
    if sort == 'price_low':
        query += ' ORDER BY (CASE WHEN sale_price IS NOT NULL AND sale_price > 0 THEN sale_price ELSE price END) ASC'
    elif sort == 'price_high':
        query += ' ORDER BY (CASE WHEN sale_price IS NOT NULL AND sale_price > 0 THEN sale_price ELSE price END) DESC'
    elif sort == 'rating':
        query += ' ORDER BY rating DESC, review_count DESC'
    elif sort == 'newest':
        query += ' ORDER BY created_at DESC'
    else:
        query += ' ORDER BY is_featured DESC, id DESC'

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    products = []
    for r in rows:
        item = dict(r)
        item['gallery_list'] = json.loads(item['gallery']) if item['gallery'] else [item['image']]
        item['colors_list'] = json.loads(item['colors']) if item['colors'] else []
        item['sizes_list'] = json.loads(item['sizes']) if item['sizes'] else []
        products.append(item)

    return jsonify({'success': True, 'count': len(products), 'products': products})

@app.route('/api/categories')
def api_get_categories():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT c.*, COUNT(p.id) as product_count
    FROM categories c
    LEFT JOIN products p ON c.id = p.category_id
    GROUP BY c.id
    ORDER BY c.id ASC
    ''')
    cats = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({'success': True, 'categories': cats})

@app.route('/api/brands')
def api_get_brands():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT DISTINCT brand FROM products WHERE brand IS NOT NULL AND brand != "" ORDER BY brand ASC')
    brands = [r['brand'] for r in c.fetchall()]
    conn.close()
    return jsonify({'success': True, 'brands': brands})

# --- Coupons API ---
@app.route('/api/coupons/validate', methods=['POST'])
def api_validate_coupon():
    data = request.get_json() or {}
    code = data.get('code', '').strip().upper()
    subtotal = float(data.get('subtotal', 0))

    if not code:
        return jsonify({'success': False, 'message': 'কুপন কোড প্রদান করুন'}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM coupons WHERE code = ? AND is_active = 1', (code,))
    coupon = c.fetchone()
    conn.close()

    if not coupon:
        return jsonify({'success': False, 'message': 'অবৈধ কুপন কোড'}), 400

    coupon = dict(coupon)

    # Check minimum spend
    if subtotal < coupon['min_spend']:
        return jsonify({
            'success': False,
            'message': f"এই কুপন ব্যবহারের জন্য সর্বনিম্ন অর্ডার পরিমাণ ৳{int(coupon['min_spend'])}"
        }), 400

    # Calculate discount
    discount = 0
    if coupon['discount_type'] == 'percentage':
        discount = (subtotal * coupon['discount_value']) / 100.0
        if coupon['max_discount'] and discount > coupon['max_discount']:
            discount = coupon['max_discount']
    else:
        discount = min(coupon['discount_value'], subtotal)

    return jsonify({
        'success': True,
        'message': f'অভিনন্দন! কুপন {code} সফলভাবে প্রয়োগ হয়েছে।',
        'code': code,
        'discount': round(discount, 2),
        'discount_type': coupon['discount_type']
    })

# --- Orders & Checkout APIs ---
@app.route('/api/orders/create', methods=['POST'])
def api_create_order():
    try:
        data = request.get_json() or {}
        customer_name = (data.get('customer_name') or '').strip()
        customer_email = (data.get('customer_email') or '').strip()
        customer_phone = (data.get('customer_phone') or '').strip()
        shipping_address = (data.get('shipping_address') or '').strip()
        shipping_district = (data.get('shipping_district') or 'Dhaka').strip()
        shipping_thana = (data.get('shipping_thana') or '').strip()
        delivery_type = (data.get('delivery_type') or 'Standard').strip()
        payment_method = (data.get('payment_method') or 'COD').strip()
        transaction_id = (data.get('transaction_id') or '').strip()
        notes = (data.get('notes') or '').strip()
        coupon_code = (data.get('coupon_code') or '').strip().upper()
        items = data.get('items', [])

        if not customer_name or not customer_phone or not shipping_address:
            return jsonify({'success': False, 'message': 'নাম, মোবাইল নম্বর এবং ঠিকানা পূরণ করুন'}), 400

        if not items or len(items) == 0:
            return jsonify({'success': False, 'message': 'আপনার কার্ট ফাঁকা'}), 400

        # Calculate totals
        subtotal = 0.0
        for item in items:
            qty = int(item.get('quantity', 1))
            price = float(item.get('price', 0))
            subtotal += (qty * price)

        # Shipping fee calculation
        is_inside_dhaka = 'dhaka' in shipping_district.lower()
        shipping_fee = 60.0 if is_inside_dhaka else 120.0
        if delivery_type == 'Express':
            shipping_fee += 60.0 # Express surcharge

        # Calculate discount from coupon
        discount = 0.0
        conn = get_db()
        c = conn.cursor()

        if coupon_code:
            c.execute('SELECT * FROM coupons WHERE code = ? AND is_active = 1', (coupon_code,))
            cpn = c.fetchone()
            if cpn:
                cpn = dict(cpn)
                if subtotal >= cpn['min_spend']:
                    if cpn['discount_type'] == 'percentage':
                        discount = (subtotal * cpn['discount_value']) / 100.0
                        if cpn['max_discount'] and discount > cpn['max_discount']:
                            discount = cpn['max_discount']
                    else:
                        discount = min(cpn['discount_value'], subtotal)
                    # Increment usage
                    c.execute('UPDATE coupons SET used_count = used_count + 1 WHERE id = ?', (cpn['id'],))

        total_amount = max(0.0, subtotal - discount + shipping_fee)

        # Generate Order Number: BB-YYYYMMDD-XXXX
        rand_suffix = random.randint(1000, 9999)
        date_str = datetime.now().strftime('%Y%m%d')
        order_number = f"BB-{date_str}-{rand_suffix}"

        # Payment Status
        payment_status = 'Paid' if payment_method in ['bKash', 'Nagad', 'Rocket', 'Card'] else 'Pending'
        order_status = 'Processing' if payment_status == 'Paid' else 'Pending'

        user_id = g.user['id'] if g.user else None

        # Insert into Orders table
        c.execute('''
        INSERT INTO orders (
            order_number, user_id, customer_name, customer_email, customer_phone,
            shipping_address, shipping_district, shipping_thana, delivery_type,
            payment_method, payment_status, transaction_id,
            subtotal, discount, shipping_fee, total_amount, coupon_code,
            order_status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_number, user_id, customer_name, customer_email, customer_phone,
            shipping_address, shipping_district, shipping_thana, delivery_type,
            payment_method, payment_status, transaction_id,
            subtotal, discount, shipping_fee, total_amount, coupon_code,
            order_status, notes
        ))
        order_id = c.lastrowid

        # Insert order items & reduce stock
        for item in items:
            prod_id = item.get('id')
            qty = int(item.get('quantity', 1))
            price = float(item.get('price', 0))
            item_total = price * qty
            c.execute('''
            INSERT INTO order_items (order_id, product_id, product_title, price, quantity, color, size, image, total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                order_id, prod_id, item.get('title', ''), price, qty,
                item.get('color', ''), item.get('size', ''), item.get('image', ''), item_total
            ))

            # Decrease product stock
            if prod_id:
                c.execute('UPDATE products SET stock = MAX(0, stock - ?) WHERE id = ?', (qty, prod_id))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'আপনার অর্ডারটি সফলভাবে সম্পন্ন হয়েছে!',
            'order_number': order_number,
            'order_id': order_id,
            'total_amount': total_amount
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'অর্ডার প্রক্রিয়াকরণে ত্রুটি: {str(e)}'}), 500

@app.route('/api/orders/track/<order_number>')
def api_track_order(order_number):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE order_number = ?', (order_number.strip().upper(),))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({'success': False, 'message': 'কোনো অর্ডার পাওয়া যায়নি। সঠিক অর্ডার নম্বর দিন'}), 404

    order = dict(row)
    c.execute('SELECT * FROM order_items WHERE order_id = ?', (order['id'],))
    order['items'] = [dict(i) for i in c.fetchall()]
    conn.close()

    # Timeline calculation based on status
    status_steps = [
        {'id': 'placed', 'name': 'অর্ডার সাবমিট', 'name_en': 'Order Placed', 'icon': 'shopping-bag'},
        {'id': 'confirmed', 'name': 'কনফার্মেশন', 'name_en': 'Confirmed', 'icon': 'check-circle'},
        {'id': 'processing', 'name': 'প্যাকিং ও প্রসেসিং', 'name_en': 'Processing', 'icon': 'package'},
        {'id': 'shipped', 'name': 'ডেলিভারিতে বের হয়েছে', 'name_en': 'Shipped', 'icon': 'truck'},
        {'id': 'delivered', 'name': 'ডেলিভারি সম্পন্ন', 'name_en': 'Delivered', 'icon': 'check'}
    ]

    # Map current order_status to active level
    status_levels = {
        'Pending': 1,
        'Processing': 2,
        'Shipped': 3,
        'Delivered': 4,
        'Cancelled': -1
    }
    current_level = status_levels.get(order['order_status'], 1)

    return jsonify({
        'success': True,
        'order': order,
        'steps': status_steps,
        'current_level': current_level
    })

@app.route('/api/orders/my-orders')
def api_my_orders():
    if not g.user:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT o.*, COUNT(oi.id) as item_count
    FROM orders o
    LEFT JOIN order_items oi ON o.id = oi.order_id
    WHERE o.user_id = ? OR o.customer_email = ?
    GROUP BY o.id
    ORDER BY o.created_at DESC
    ''', (g.user['id'], g.user['email']))
    orders = [dict(r) for r in c.fetchall()]

    for o in orders:
        c.execute('SELECT * FROM order_items WHERE order_id = ?', (o['id'],))
        o['items'] = [dict(i) for i in c.fetchall()]

    conn.close()
    return jsonify({'success': True, 'orders': orders})

# --- Reviews API ---
@app.route('/api/reviews', methods=['POST'])
def api_add_review():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    rating = int(data.get('rating', 5))
    comment = data.get('comment', '').strip()
    user_name = data.get('user_name', '').strip()
    image_url = data.get('image_url', None)

    if not product_id or not comment:
        return jsonify({'success': False, 'message': 'মতামত এবং রেটিং প্রদান করুন'}), 400

    if not user_name:
        user_name = g.user['name'] if g.user else 'সম্মানিত ক্রেতা'

    user_id = g.user['id'] if g.user else None

    conn = get_db()
    c = conn.cursor()
    c.execute('''
    INSERT INTO reviews (product_id, user_id, user_name, rating, comment, image_url, verified_purchase)
    VALUES (?, ?, ?, ?, ?, ?, 1)
    ''', (product_id, user_id, user_name, rating, comment, image_url))

    # Recalculate product rating
    c.execute('SELECT AVG(rating) as avg_rating, COUNT(*) as cnt FROM reviews WHERE product_id = ?', (product_id,))
    stats = c.fetchone()
    avg_r = round(float(stats['avg_rating']), 1) if stats['avg_rating'] else rating
    cnt = stats['cnt']

    c.execute('UPDATE products SET rating = ?, review_count = ? WHERE id = ?', (avg_r, cnt, product_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'আপনার মূল্যবান পর্যালোচনার জন্য ধন্যবাদ!'})

@app.route('/api/reviews/<int:review_id>/helpful', methods=['POST'])
def api_helpful_review(review_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE reviews SET helpful_count = helpful_count + 1 WHERE id = ?', (review_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# --- Wishlist APIs ---
@app.route('/api/wishlist')
def api_get_wishlist():
    if not g.user:
        return jsonify({'success': True, 'items': []})

    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT p.* FROM wishlist w
    JOIN products p ON w.product_id = p.id
    WHERE w.user_id = ?
    ORDER BY w.created_at DESC
    ''', (g.user['id'],))
    items = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({'success': True, 'items': items})

@app.route('/api/wishlist/toggle', methods=['POST'])
def api_toggle_wishlist():
    if not g.user:
        return jsonify({'success': False, 'message': 'উইশলিস্ট সংরক্ষণের জন্য অনুগ্রহ করে লগইন করুন'}), 401

    data = request.get_json() or {}
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'success': False, 'message': 'Product ID required'}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id FROM wishlist WHERE user_id = ? AND product_id = ?', (g.user['id'], product_id))
    exists = c.fetchone()

    if exists:
        c.execute('DELETE FROM wishlist WHERE id = ?', (exists['id'],))
        in_wishlist = False
        msg = 'উইশলিস্ট থেকে মুছে ফেলা হয়েছে'
    else:
        c.execute('INSERT INTO wishlist (user_id, product_id) VALUES (?, ?)', (g.user['id'], product_id))
        in_wishlist = True
        msg = 'উইশলিস্টে যুক্ত হয়েছে'

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'in_wishlist': in_wishlist, 'message': msg})

# --- Contact API ---
@app.route('/api/contact', methods=['POST'])
def api_contact():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()

    if not name or not email or not message:
        return jsonify({'success': False, 'message': 'নাম, ইমেইল এবং বার্তা পূরণ করুন'}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute('''
    INSERT INTO contact_messages (name, email, phone, subject, message)
    VALUES (?, ?, ?, ?, ?)
    ''', (name, email, phone, subject, message))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'আপনার বার্তাটি সফলভাবে পাঠানো হয়েছে। আমরা শীঘ্রই যোগাযোগ করবো!'})

# ==========================================
# ADMIN BACKEND APIs
# ==========================================

@app.route('/api/admin/stats')
@admin_required
def api_admin_stats():
    conn = get_db()
    c = conn.cursor()

    # Total Sales
    c.execute('SELECT COALESCE(SUM(total_amount), 0) as total_sales FROM orders WHERE order_status != "Cancelled"')
    total_sales = float(c.fetchone()['total_sales'])

    # Total Orders
    c.execute('SELECT COUNT(*) as total_orders FROM orders')
    total_orders = int(c.fetchone()['total_orders'])

    # Pending Orders
    c.execute('SELECT COUNT(*) as pending_orders FROM orders WHERE order_status = "Pending"')
    pending_orders = int(c.fetchone()['pending_orders'])

    # Today's Orders & Sales
    today_prefix = datetime.now().strftime('%Y-%m-%d')
    c.execute('SELECT COUNT(*) as cnt, COALESCE(SUM(total_amount), 0) as rev FROM orders WHERE created_at LIKE ?', (f'{today_prefix}%',))
    today_stats = c.fetchone()
    today_orders = int(today_stats['cnt'])
    today_sales = float(today_stats['rev'])

    # Total Registered Customers
    c.execute('SELECT COUNT(*) as total_customers FROM users WHERE role = "customer"')
    total_customers = int(c.fetchone()['total_customers'])

    # Low Stock Products (< 10)
    c.execute('SELECT COUNT(*) as low_stock FROM products WHERE stock < 10')
    low_stock = int(c.fetchone()['low_stock'])

    # Recent 6 Orders
    c.execute('SELECT * FROM orders ORDER BY created_at DESC LIMIT 6')
    recent_orders = [dict(r) for r in c.fetchall()]

    # Top Selling Products (ordered by review count/mock logic)
    c.execute('SELECT id, title, price, sale_price, stock, image, review_count FROM products ORDER BY review_count DESC LIMIT 5')
    top_products = [dict(r) for r in c.fetchall()]

    # Monthly revenue data for Chart.js
    chart_labels = ['মে', 'জুন', 'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর']
    chart_data = [45000, 68000, 89000, 115000, 142000, 178000, total_sales + 120000]

    conn.close()

    return jsonify({
        'success': True,
        'stats': {
            'total_sales': round(total_sales, 2),
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'today_orders': today_orders,
            'today_sales': round(today_sales, 2),
            'total_customers': total_customers,
            'low_stock': low_stock
        },
        'chart': {
            'labels': chart_labels,
            'data': chart_data
        },
        'recent_orders': recent_orders,
        'top_products': top_products
    })

@app.route('/api/admin/products', methods=['GET', 'POST'])
@admin_required
def api_admin_products():
    conn = get_db()
    c = conn.cursor()

    if request.method == 'POST':
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        title_bn = data.get('title_bn', '').strip()
        category_id = int(data.get('category_id', 1))
        brand = data.get('brand', '').strip()
        price = float(data.get('price', 0))
        sale_price = float(data.get('sale_price')) if data.get('sale_price') else None
        stock = int(data.get('stock', 10))
        sku = data.get('sku', '').strip() or f"PROD-{random.randint(1000, 9999)}"
        image = data.get('image', '').strip() or 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800'
        description = data.get('description', '').strip()
        description_bn = data.get('description_bn', '').strip()
        colors = json.dumps(data.get('colors', []))
        sizes = json.dumps(data.get('sizes', []))
        is_featured = 1 if data.get('is_featured') else 0
        is_flash_sale = 1 if data.get('is_flash_sale') else 0

        # Fetch category name
        c.execute('SELECT name FROM categories WHERE id = ?', (category_id,))
        cat_row = c.fetchone()
        category_name = cat_row['name'] if cat_row else 'General'

        slug = title.lower().replace(' ', '-').replace('/', '-')[:60] + f"-{random.randint(100, 999)}"

        c.execute('''
        INSERT INTO products (
            title, title_bn, slug, category_id, category_name, brand,
            description, description_bn, price, sale_price, stock, sku,
            image, colors, sizes, is_featured, is_flash_sale
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            title, title_bn, slug, category_id, category_name, brand,
            description, description_bn, price, sale_price, stock, sku,
            image, colors, sizes, is_featured, is_flash_sale
        ))
        conn.commit()
        new_id = c.lastrowid
        conn.close()
        return jsonify({'success': True, 'message': 'নতুন পণ্য সফলভাবে যুক্ত করা হয়েছে!', 'id': new_id})

    # GET All Products
    c.execute('SELECT * FROM products ORDER BY id DESC')
    products = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({'success': True, 'products': products})

@app.route('/api/admin/products/<int:prod_id>', methods=['PUT', 'DELETE'])
@admin_required
def api_admin_product_detail(prod_id):
    conn = get_db()
    c = conn.cursor()

    if request.method == 'DELETE':
        c.execute('DELETE FROM products WHERE id = ?', (prod_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'পণ্য সফলভাবে মুছে ফেলা হয়েছে'})

    # PUT: Edit product
    data = request.get_json() or {}
    c.execute('''
    UPDATE products SET
        title = ?, title_bn = ?, brand = ?, price = ?, sale_price = ?,
        stock = ?, is_featured = ?, is_flash_sale = ?, description = ?
    WHERE id = ?
    ''', (
        data.get('title'), data.get('title_bn'), data.get('brand'),
        float(data.get('price', 0)), float(data.get('sale_price')) if data.get('sale_price') else None,
        int(data.get('stock', 0)), 1 if data.get('is_featured') else 0,
        1 if data.get('is_flash_sale') else 0, data.get('description'), prod_id
    ))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'পণ্য সফলভাবে আপডেট করা হয়েছে'})

@app.route('/api/admin/orders')
@admin_required
def api_admin_orders():
    conn = get_db()
    c = conn.cursor()
    status_filter = request.args.get('status', '').strip()

    if status_filter and status_filter != 'all':
        c.execute('SELECT * FROM orders WHERE order_status = ? ORDER BY created_at DESC', (status_filter,))
    else:
        c.execute('SELECT * FROM orders ORDER BY created_at DESC')

    orders = [dict(r) for r in c.fetchall()]
    for o in orders:
        c.execute('SELECT * FROM order_items WHERE order_id = ?', (o['id'],))
        o['items'] = [dict(i) for i in c.fetchall()]

    conn.close()
    return jsonify({'success': True, 'orders': orders})

@app.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
@admin_required
def api_admin_update_order_status(order_id):
    data = request.get_json() or {}
    new_status = data.get('status', '').strip()
    notes = data.get('notes', '').strip()

    valid_statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': 'অবৈধ স্ট্যাটাস'}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute('''
    UPDATE orders SET order_status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (new_status, notes, order_id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': f'অর্ডার স্ট্যাটাস সফলভাবে {new_status} করা হয়েছে'})

@app.route('/api/admin/customers')
@admin_required
def api_admin_customers():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT u.id, u.name, u.email, u.phone, u.district, u.created_at,
           COUNT(o.id) as order_count,
           COALESCE(SUM(o.total_amount), 0) as total_spent
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.role = 'customer'
    GROUP BY u.id
    ORDER BY u.created_at DESC
    ''')
    customers = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({'success': True, 'customers': customers})

@app.route('/api/admin/coupons', methods=['GET', 'POST'])
@admin_required
def api_admin_coupons():
    conn = get_db()
    c = conn.cursor()

    if request.method == 'POST':
        data = request.get_json() or {}
        code = data.get('code', '').strip().upper()
        discount_type = data.get('discount_type', 'percentage')
        discount_value = float(data.get('discount_value', 0))
        min_spend = float(data.get('min_spend', 0))
        max_discount = float(data.get('max_discount')) if data.get('max_discount') else None
        expiry_date = data.get('expiry_date', '')
        usage_limit = int(data.get('usage_limit', 100))

        if not code or discount_value <= 0:
            return jsonify({'success': False, 'message': 'কুপন কোড ও ডিসকাউন্ট ভ্যালু দিন'}), 400

        c.execute('''
        INSERT INTO coupons (code, discount_type, discount_value, min_spend, max_discount, expiry_date, usage_limit)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (code, discount_type, discount_value, min_spend, max_discount, expiry_date, usage_limit))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'নতুন কুপন সফলভাবে তৈরি করা হয়েছে!'})

    c.execute('SELECT * FROM coupons ORDER BY id DESC')
    coupons = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({'success': True, 'coupons': coupons})

@app.route('/api/admin/coupons/<int:coupon_id>', methods=['DELETE'])
@admin_required
def api_admin_delete_coupon(coupon_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM coupons WHERE id = ?', (coupon_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'কুপন মুছে ফেলা হয়েছে'})

# Run server
if __name__ == '__main__':
    print("Starting BongoBazaar server on http://127.0.0.1:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
