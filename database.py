"""
Database setup, schema creation, and admin isolation for BongoBazaar E-Commerce platform.
"""
import sqlite3
import os
import json
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash

# Database location. On Render the file lives on the persistent disk:
# set DATABASE_PATH=/var/data/bongobazaar.db in the Render env vars
# (see render.yaml). Locally it defaults to bongobazaar.db next to
# this file. Never commit the live database file to git.
DB_PATH = os.environ.get('DATABASE_PATH') or os.path.join(os.path.dirname(__file__), 'bongobazaar.db')

def hash_password(password: str) -> str:
    # Salted, slow hash (Werkzeug / pbkdf2). Never store plain SHA256 hashes.
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return check_password_hash(password_hash, password)
    except Exception:
        return False

def get_db():
    # Make sure the database directory exists (e.g. the Render disk
    # mount /var/data) so the first connect does not fail.
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
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
        shipping_division TEXT,
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

    # Safe Schema Migrations
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN shipping_division TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN division TEXT")
    except Exception:
        pass

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

    # 11. Site Settings Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS site_settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

DEFAULT_SETTINGS = {
    'shop_name': 'BongoBazaar',
    'shop_name_bn': 'বঙ্গবাজার',
    'shop_tagline': 'সেরা মানের দেশি ও প্রয়োজনীয় পণ্য, এখন এক ক্লিকেই!',
    'shop_description': 'সারা দেশে দ্রুততম ক্যাশ অন ডেলিভারি এবং সহজ কেনাকাটার নির্ভরযোগ্য প্ল্যাটফর্ম।',
    'contact_phone': '01700-000000',
    'contact_email': 'support@bongobazaar.com',
    'contact_address': 'বাড়ি ১২, রোড ৪, ধানমন্ডি, ঢাকা-১২০৫',
    'whatsapp_number': '01700000000',
    'business_hours': 'সকাল ৯:০০ - রাত ১০:০০ (প্রতিদিন)',
    'shipping_fee_dhaka': '60',
    'shipping_fee_outside': '120',
    'free_shipping_threshold': '0',
    'facebook_url': 'https://facebook.com',
    'instagram_url': 'https://instagram.com',
    'youtube_url': 'https://youtube.com',
    'announcement_enabled': '0',
    'announcement_text': 'আমাদের সকল অর্গানিক ও নিত্যপ্রয়োজনীয় পণ্যে ক্যাশ অন ডেলিভারি সুবিধা উপভোগ করুন!',
    'currency_symbol': '৳',
    'delivery_time_inside': '২৪ থেকে ৪৮ ঘণ্টা',
    'delivery_time_outside': '২ থেকে ৩ কার্যদিবস'
}

def get_all_settings():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT key, value FROM site_settings')
    rows = cursor.fetchall()
    conn.close()

    settings = dict(DEFAULT_SETTINGS)
    for r in rows:
        settings[r['key']] = r['value']
    return settings

def update_site_settings(new_settings: dict):
    conn = get_db()
    cursor = conn.cursor()
    for key, value in new_settings.items():
        cursor.execute('''
        INSERT INTO site_settings (key, value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
        ''', (key, str(value)))
    conn.commit()
    conn.close()
    return get_all_settings()

def seed_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Seed Dedicated Admin (if not exists)
    cursor.execute('SELECT COUNT(*) as cnt FROM admin_users')
    if cursor.fetchone()['cnt'] == 0:
        admin_password = os.environ.get('ADMIN_PASSWORD')
        if not admin_password:
            print("No admin user created: set ADMIN_PASSWORD env var once to create the first admin.")
        else:
            admin_pw = hash_password(admin_password)
            cursor.execute('''
            INSERT INTO admin_users (username, email, password_hash, name, role)
            VALUES (?, ?, ?, ?, ?)
            ''', ('admin', 'admin@bongobazaar.com', admin_pw, 'সুপার অ্যাডমিন (Admin)', 'superadmin'))
            print("Dedicated Admin user created: username='admin' (password from ADMIN_PASSWORD env var)")

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

    # Clean any demo coupons
    cursor.execute('DELETE FROM coupons')

    # 3. Seed Default Site Settings (if missing)
    for k, v in DEFAULT_SETTINGS.items():
        cursor.execute('''
        INSERT INTO site_settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO NOTHING
        ''', (k, v))

    conn.commit()
    conn.close()

def clear_demo_data():
    """Purges all demo data from database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM order_items")
    cursor.execute("DELETE FROM reviews")
    cursor.execute("DELETE FROM wishlist")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM coupons")
    conn.commit()
    conn.close()
    print("All demo data successfully purged!")

if __name__ == '__main__':
    init_db()
    seed_db()
