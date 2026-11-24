"""
Database setup, schema creation, and admin isolation for BongoBazaar E-Commerce platform.
"""
import sqlite3
import os
import json
import hashlib
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), 'bongobazaar.db')

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Dedicated Admin Users Table (Completely separate from customer users)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT DEFAULT 'superadmin',
        avatar_url TEXT,
        last_login TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. Customers / Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'customer',
        address TEXT,
        city TEXT,
        district TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 3. Categories Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        name_bn TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        icon TEXT,
        image_url TEXT,
        description TEXT
    )
    ''')

    # 4. Products Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        title_bn TEXT,
        slug TEXT UNIQUE,
        category_id INTEGER,
        category_name TEXT,
        brand TEXT,
        description TEXT,
        description_bn TEXT,
        price REAL NOT NULL,
        sale_price REAL,
        stock INTEGER DEFAULT 10,
        sku TEXT UNIQUE,
        image TEXT NOT NULL,
        gallery TEXT,
        colors TEXT,
        sizes TEXT,
        is_featured INTEGER DEFAULT 0,
        is_flash_sale INTEGER DEFAULT 0,
        rating REAL DEFAULT 5.0,
        review_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
    ''')

    # 5. Orders Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE NOT NULL,
        user_id INTEGER,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        shipping_address TEXT NOT NULL,
        shipping_district TEXT NOT NULL,
        shipping_thana TEXT,
        delivery_type TEXT DEFAULT 'Standard',
        payment_method TEXT NOT NULL,
        payment_status TEXT DEFAULT 'Pending',
        transaction_id TEXT,
        subtotal REAL NOT NULL,
        discount REAL DEFAULT 0,
        shipping_fee REAL NOT NULL,
        total_amount REAL NOT NULL,
        coupon_code TEXT,
        order_status TEXT DEFAULT 'Pending',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # 6. Order Items Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_title TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        color TEXT,
        size TEXT,
        image TEXT,
        total REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')

    # 7. Reviews Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        user_id INTEGER,
        user_name TEXT NOT NULL,
        rating INTEGER NOT NULL,
        comment TEXT NOT NULL,
        image_url TEXT,
        helpful_count INTEGER DEFAULT 0,
        verified_purchase INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
    )
    ''')

    # 8. Coupons Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        discount_type TEXT NOT NULL, -- 'percentage' or 'fixed'
        discount_value REAL NOT NULL,
        min_spend REAL DEFAULT 0,
        max_discount REAL,
        expiry_date TEXT,
        usage_limit INTEGER DEFAULT 100,
        used_count INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 9. Wishlist Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, product_id)
    )
    ''')

    # 10. Contact Messages Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contact_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        subject TEXT,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'Unread',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

def seed_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Seed Dedicated Admin (if not exists)
    cursor.execute('SELECT COUNT(*) as cnt FROM admin_users')
    if cursor.fetchone()['cnt'] == 0:
        admin_pw = hash_password('Admin@12345')
        cursor.execute('''
        INSERT INTO admin_users (username, email, password_hash, name, role)
        VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@bongobazaar.com', admin_pw, 'সুপার অ্যাডমিন (Admin)', 'superadmin'))
        print("Dedicated Admin user created: username='admin', password='Admin@12345'")

    # Ensure no admin exists in customer users table
    cursor.execute("DELETE FROM users WHERE role = 'admin'")

    # 2. Seed Default Categories (for product organization)
    cursor.execute('SELECT COUNT(*) as cnt FROM categories')
    if cursor.fetchone()['cnt'] == 0:
        categories = [
            ('Fashion & Clothing', 'ফ্যাশন ও পোশাক', 'fashion', 'shirt', 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=600&auto=format&fit=crop&q=80', 'Traditional and modern Bangladeshi wear for Men, Women & Kids'),
            ('Electronics & Gadgets', 'ইলেকট্রনিক্স ও গ্যাজেট', 'electronics', 'smartphone', 'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=600&auto=format&fit=crop&q=80', 'Smartphones, Smart TVs, Laptops and audio accessories'),
            ('Groceries & Organic', 'মুদি ও খাঁটি অর্গানিক', 'groceries', 'apple', 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=600&auto=format&fit=crop&q=80', 'Pure mustard oil, honey, premium rice, spices & dry fruits'),
            ('Beauty & Cosmetics', 'সৌন্দর্য ও রূপচর্চা', 'beauty', 'sparkles', 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=600&auto=format&fit=crop&q=80', 'Halal skincare, organic oils, lipsticks and beauty essentials'),
            ('Home & Living', 'হোম ও কিচেন', 'home-living', 'home', 'https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?w=600&auto=format&fit=crop&q=80', 'Kitchen appliances, cookware, bedsheets & home decor'),
            ('Health & Wellness', 'স্বাস্থ্য ও ফিটনেস', 'health', 'heart-pulse', 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600&auto=format&fit=crop&q=80', 'Vitamins, supplements, herbal tonics, and protective gear')
        ]
        for cat in categories:
            cursor.execute('''
            INSERT INTO categories (name, name_bn, slug, icon, image_url, description)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', cat)

    # 3. Seed Default Coupons (if empty)
    cursor.execute('SELECT COUNT(*) as cnt FROM coupons')
    if cursor.fetchone()['cnt'] == 0:
        now = datetime.now()
        coupons = [
            ('EID20', 'percentage', 20.0, 500.0, 1500.0, (now + timedelta(days=60)).strftime('%Y-%m-%d'), 200, 1),
            ('WELCOME50', 'fixed', 50.0, None, 500.0, (now + timedelta(days=90)).strftime('%Y-%m-%d'), 500, 1),
            ('BONGO100', 'fixed', 100.0, None, 1000.0, (now + timedelta(days=30)).strftime('%Y-%m-%d'), 100, 1)
        ]
        for c in coupons:
            cursor.execute('''
            INSERT INTO coupons (code, discount_type, discount_value, max_discount, min_spend, expiry_date, usage_limit, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', c)

    # NOTE: NO DEMO PRODUCTS are seeded! All demo products are removed.
    conn.commit()
    conn.close()

def clear_demo_data():
    """Purges all demo products, reviews, wishlist, and demo order items from database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM order_items")
    cursor.execute("DELETE FROM reviews")
    cursor.execute("DELETE FROM wishlist")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM users WHERE role = 'admin'")
    conn.commit()
    conn.close()
    print("All demo products and related demo data successfully purged!")

if __name__ == '__main__':
    init_db()
    seed_db()
