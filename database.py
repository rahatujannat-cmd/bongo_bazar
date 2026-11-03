"""
Database setup, schema creation, and realistic seeding for BongoBazaar E-Commerce platform.
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

    # Users Table
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

    # Categories Table
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

    # Products Table
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
        rating REAL DEFAULT 4.8,
        review_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
    ''')

    # Orders Table
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

    # Order Items Table
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

    # Reviews Table
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

    # Coupons Table
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

    # Wishlist Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, product_id)
    )
    ''')

    # Contact Messages Table
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

    # Check if already seeded
    cursor.execute('SELECT COUNT(*) as cnt FROM products')
    if cursor.fetchone()['cnt'] > 0:
        conn.close()
        return

    print("Seeding BongoBazaar database with realistic Bangladeshi products and demo data...")

    # 1. Seed Users (Admin & Sample Customer)
    admin_pw = hash_password('admin123')
    user_pw = hash_password('customer123')
    
    cursor.execute('''
    INSERT OR IGNORE INTO users (name, email, phone, password_hash, role, address, city, district)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('মারুফ আহমেদ (Admin)', 'admin@bongobazaar.com', '01711000001', admin_pw, 'admin', 'হাউজ ১২, রোড ৫, ধানমন্ডি', 'ঢাকা', 'Dhaka'))

    cursor.execute('''
    INSERT OR IGNORE INTO users (name, email, phone, password_hash, role, address, city, district)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('তানভীর হোসেন (Customer)', 'customer@bongobazaar.com', '01819000002', user_pw, 'customer', 'ফ্ল্যাট ৪বি, বনানী ব্লক-সি', 'ঢাকা', 'Dhaka'))

    # 2. Seed Categories
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

    # 3. Seed Products
    products = [
        # Fashion
        (
            'Aarong Style Premium Silk Embroidered Panjabi',
            'আড়ং স্টাইল প্রিমিয়াম সিল্ক কারুকাজ করা পাঞ্জাবি',
            'aarong-style-premium-silk-panjabi',
            1, 'Fashion & Clothing', 'Aarong Luxe',
            'Crafted from 100% pure silk with intricate metallic thread embroidery along the collar and placket. Ideal for Eid, weddings, and special festivities.',
            'খাঁটি সিল্ক কাপড়ের ওপর আকর্ষণীয় সোনালি সুতার সূক্ষ্ম কারুকাজ। ঈদ, গায়ে হলুদ কিংবা বিশেষ উৎসবের জন্য চমৎকার ও আভিজাত্যপূর্ণ পোশাক।',
            4500.0, 3600.0, 15, 'PAN-SLK-01',
            'https://images.unsplash.com/photo-1617127365659-c47fa864d8bc?w=800&auto=format&fit=crop&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1617127365659-c47fa864d8bc?w=800&auto=format&fit=crop&q=80',
                'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800&auto=format&fit=crop&q=80'
            ]),
            json.dumps(['Navy Blue', 'Maroon', 'Emerald Green', 'Royal Black']),
            json.dumps(['M (38)', 'L (40)', 'XL (42)', 'XXL (44)']),
            1, 1, 4.9, 42
        ),
        (
            'Traditional Tangail Soft Cotton Handloom Saree',
            'ঐতিহ্যবাহী টাঙ্গাইল সফট সুতি হ্যান্ডলুম শাড়ি',
            'tangail-soft-cotton-handloom-saree',
            1, 'Fashion & Clothing', 'Tangail Weaves',
            'Authentic Tangail taat saree woven from high thread count fine cotton. Comes with unstitched matching blouse piece, breathable and graceful.',
            'টাঙ্গাইলের দক্ষ তাঁতীদের বোনা ১০০% খাঁটি সুতি শাড়ি। হালকা, আরামদায়ক ও গরমের দিনে পরার জন্য সেরা। সাথে ম্যাচিং ব্লাউজ পিস অন্তর্ভুক্ত।',
            2200.0, 1750.0, 24, 'SAR-TNG-02',
            'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&auto=format&fit=crop&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&auto=format&fit=crop&q=80'
            ]),
            json.dumps(['Mustard Yellow', 'Crimson Red', 'Pastel Pink']),
            json.dumps(['Free Size (12 Haat)']),
            1, 0, 4.8, 38
        ),
        (
            'Apex Handcrafted Genuine Leather Formal Oxford Shoes',
            'এপেক্স জেনুইন লেদার ফর্মাল অক্সফোর্ড জুতো',
            'apex-leather-formal-oxford-shoes',
            1, 'Fashion & Clothing', 'Apex',
            'Premium full-grain leather outer with padded insole for all-day comfort. Anti-skid rubber sole suitable for office and ceremonies.',
            'খাঁটি চামড়ায় তৈরি টেকসই ফর্মাল জুতো। সফট কুশন ইনসোল সারাদিন স্বাচ্ছন্দ্য দেয়। অফিস কিংবা অনুষ্ঠানে ব্যবহারের জন্য মানানসই।',
            4890.0, 3990.0, 12, 'SHOE-APX-03',
            'https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=800&auto=format&fit=crop&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=800&auto=format&fit=crop&q=80'
            ]),
            json.dumps(['Glossy Black', 'Deep Brown', 'Tan']),
            json.dumps(['40', '41', '42', '43', '44']),
            0, 1, 4.7, 19
        ),
        (
            'Dhakaia Jamdani Fine Silk Saree - Heritage Collection',
            'ঢাকাই জামদানি ফাইন সিল্ক শাড়ি - ঐতিহ্যবাহী কালেকশন',
            'dhakaia-jamdani-fine-silk-saree',
            1, 'Fashion & Clothing', 'Jamdani Heritage',
            'Geographical Indication (GI) certified hand-woven Jamdani saree with exquisite floral buta and jhalar motifs. Pure heritage art.',
            'বাংলাদেশের ঐতিহ্যবাহী জিআই পণ্য ঢাকাই জামদানি। সূক্ষ্ম নকশা ও নিখুঁত সুতার বয়নে তৈরি রাজকীয় শাড়ি।',
            8500.0, 6990.0, 8, 'SAR-JAM-04',
            'https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=800&auto=format&fit=crop&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=800&auto=format&fit=crop&q=80'
            ]),
            json.dumps(['Royal Red & Gold', 'Black & Silver', 'Emerald Green']),
            json.dumps(['Standard (12 Haat)']),
            1, 0, 5.0, 27
        ),

        # Electronics
        (
            'Walton 43-Inch 4K Frameless Google Smart Android TV',
            'ওয়ালটন ৪৩ ইঞ্চি ৪কে ফ্রেমলেস গুগল স্মার্ট টিভি',
            'walton-43-inch-4k-smart-tv',
            2, 'Electronics & Gadgets', 'Walton',
            '4K UHD display with HDR10+, Dolby Audio 20W speakers, Voice remote, Google TV OS with licensed Netflix, YouTube, and Prime Video.',
            'ওয়ালটনের লেটেস্ট ৪কে ইউএইচডি ফ্রেমলেস ডিসপ্লে। ডলবি অডিও সিস্টেম, গুগল ভয়েস রিমোট ও ৫ বছরের প্যানেল ওয়ারেন্টিসহ জেনুইন স্মার্ট টিভি।',
            38500.0, 32990.0, 10, 'TV-WLT-43',
            'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&auto=format&fit=crop&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&auto=format&fit=crop&q=80'
            ]),
            json.dumps(['Midnight Black']),
            json.dumps(['43-Inch', '50-Inch']),
            1, 1, 4.8, 64
        ),
        (
            'Samsung Galaxy A55 5G (8GB RAM / 128GB ROM)',
            'স্যামসাং গ্যালাক্সি এ৫৫ ৫জি (৮জিবি র‍্যাম / ১২৮জিবি রোম)',
            'samsung-galaxy-a55-5g',
            2, 'Electronics & Gadgets', 'Samsung',
            'Super AMOLED 120Hz display, 50MP OIS camera, 5000mAh battery with 25W fast charging, IP67 water and dust resistance, Official BD Warranty.',
            'অফিসিয়াল ১ বছরের ওয়ারেন্টিসহ সুপার অ্যামোলেড ১২০ হার্জ ডিসপ্লে, ৫০ মেগাপিক্সেল ওআইএস ট্রিপল ক্যামেরা এবং ৫০০০ মিলিঅ্যাম্পিয়ার ব্যাটারি।',
            48999.0, 44500.0, 18, 'SAM-A55-128',
            'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=80'
            ]),
            json.dumps(['Awesome Navy', 'Awesome Iceblue', 'Awesome Lilac']),
            json.dumps(['8GB/128GB', '8GB/256GB']),
            1, 0, 4.9, 115
        ),
        (
            'Realme Buds Air 6 Pro Wireless ANC Earbuds',
            'রিয়েলমি বাডস এয়ার ৬ প্রো ওয়্যারলেস ব্লুটুথ ইয়ারবাডস',
            'realme-buds-air-6-pro-anc',
            2, 'Electronics & Gadgets', 'Realme',
            '50dB Active Noise Cancellation, Hi-Res LDAC Audio, 40 hours battery life with charging case, Dual device connection.',
            '৫০ ডেসিবেল নয়েজ ক্যান্সেলেশন, হাই-রেস এলডিএসি কোডেক অডিও এবং দীর্ঘ ৪০ ঘণ্টার ব্যাটারি ব্যাকআপ। গেমিং ও মিউজিকের জন্য সেরা পছন্দ।',
            5490.0, 4290.0, 30, 'EAR-RLM-06',
            'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop&q=80'
            ]),
            json.dumps(['Titanium Silver', 'Glacier White']),
            json.dumps(['Standard']),
            0, 1, 4.7, 53
        ),
        (
            'Baseus 20000mAh 65W PD Fast Charging Power Bank',
            'বেসাস ২০০০০ এমএএইচ ৬৫ ওয়াট ফাস্ট চার্জিং পাওয়ার ব্যাংক',
            'baseus-20000mah-65w-powerbank',
            2, 'Electronics & Gadgets', 'Baseus',
            'Can charge MacBook, laptops and flagship smartphones simultaneously. Digital LED display showing voltage and remaining power.',
            'ল্যাপটপ ও স্মার্টফোন একসাথে দ্রুত চার্জ করার সুবিধা। ডিজিটাল ডিসপ্লেতে চার্জ ও ভোল্টেজ দেখার সুবিধা। ২০০০০ মিলিঅ্যাম্পিয়ার ক্যাপাসিটি।',
            4200.0, 3450.0, 22, 'POW-BAS-20',
            'https://images.unsplash.com/photo-1609592426861-f3b39cb9588b?w=800&auto=format&fit=crop&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1609592426861-f3b39cb9588b?w=800&auto=format&fit=crop&q=80'
            ]),
            json.dumps(['Matte Black', 'Snow White']),
            json.dumps(['20000 mAh']),
            0, 0, 4.8, 31
        ),

        # Groceries & Organic
        (
            'Kazi Farms Organic Sundarban Natural Raw Honey (500g)',
            'কাজী ফার্মস সুন্দরবনের প্রাকৃতিক খাঁটি মধু (৫০০ গ্রাম)',
            'sundarban-natural-raw-honey-500g',
            3, 'Groceries & Organic', 'Kazi Organic',
            'Directly sourced from Sundarban mangrove forest. Unprocessed, 100% pure raw wild flower honey packed with antioxidants and natural pollen.',
            'সুন্দরবনের গভীর জঙ্গল থেকে সংগৃহীত ১০০% নির্ভেজাল ও প্রাকৃতিক চাকের মধু। কোনো কেমিক্যাল বা প্রিজারভেটিভ নেই। রোগ প্রতিরোধে দারুণ।',
            850.0, 720.0, 40, 'GRO-HNY-500',
            'https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=800&auto=format&fit=crop&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=800&auto=format&fit=crop&q=80'
            ]),
            json.dumps(['Golden Amber']),
            json.dumps(['500g', '1kg']),
            1, 0, 4.9, 87
        ),
        (
            'Traditional Cold-Pressed Pure Mustard Oil - 1 Litre',
            'ঘানি ভাঙা খাঁটি সরিষার তেল - ১ লিটার',
            'cold-pressed-pure-mustard-oil-1l',
            3, 'Groceries & Organic', 'Khati Organics',
            'Wooden expeller (ghani) pressed authentic mustard oil with strong natural pungency. Chemical-free, ideal for cooking and bhorta.',
            'কাঠের ঘানিতে ভাঙা খাঁটি দেশি সরিষার ঝাঁঝালো তেল। ভর্তা, রান্না ও আচার তৈরির জন্য সেরা। সম্পূর্ণ ভেজালমুক্ত ও স্বাস্থ্যকর।',
            380.0, 310.0, 60, 'GRO-OIL-01',
            'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=800&auto=format&fit=crop&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=800&auto=format&fit=crop&q=80'
            ]),
            json.dumps(['Natural Mustard']),
            json.dumps(['1 Litre', '2 Litre', '5 Litre']),
            1, 1, 4.8, 92
        ),
        (
            'Dinajpur Premium Chinigura Aromatic Rice (5 Kg)',
            'দিনাজপুরের প্রিমিয়াম চিনিগুঁড়া সুগন্ধি পোলাও চাল (৫ কেজি)',
            'dinajpur-chinigura-aromatic-rice-5kg',
            3, 'Groceries & Organic', 'Deshi Krishi',
            'Old vintage aromatic Chinigura rice from Dinajpur. Perfectly aged, delicate fragrance, ideal for Biryani, Polao, and Payesh.',
            'দিনাজপুরের বাছাইকৃত পুরাতন চিনিগুঁড়া চাল। চমৎকার সুবাস ও লম্বা দানাদার। বিরিয়ানি, পোলাও ও পায়েশ রান্নার জন্য অসাধারণ।',
            750.0, 680.0, 50, 'GRO-RIC-05',
            'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=800&auto=format&fit=crop&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=800&auto=format&fit=crop&q=80'
            ]),
            json.dumps(['White']),
            json.dumps(['5 Kg', '10 Kg']),
            0, 0, 4.9, 65
        ),

        # Beauty & Cosmetics
        (
            'Lafz Halal Velvet Matte Liquid Lipstick (BD Shades)',
            'লাফজ হালাল ভেলভেট ম্যাট লিকুইড লিপস্টিক',
            'lafz-halal-velvet-matte-lipstick',
            4, 'Beauty & Cosmetics', 'Lafz Halal',
            '100% Halal certified, alcohol-free and paraben-free matte liquid lipstick. Transfer-proof formula that stays vibrant for 12 hours.',
            '১০০% হালাল সনদপ্রাপ্ত, অ্যালকোহল ও প্যারাবেন মুক্ত। ১২ ঘণ্টা পর্যন্ত স্থায়ী ওয়াটারপ্রুফ ফর্মুলা, যা ঠোঁটকে মসৃণ ও আকর্ষণীয় রাখে।',
            750.0, 599.0, 35, 'BEA-LFZ-LIP',
            'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=800&auto=format&fit=crop&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=800&auto=format&fit=crop&q=80'
            ]),
            json.dumps(['Ruby Crimson', 'Rosy Nude', 'Mocha Brown']),
            json.dumps(['5ml']),
            1, 1, 4.7, 78
        ),
        (
            'Organic Cold Pressed Moroccan Argan Hair & Face Oil (100ml)',
            'অর্গানিক কোল্ড প্রেসড মরোক্কান আরগান অয়েল (১০০ মি.লি.)',
            'organic-moroccan-argan-oil-100ml',
            4, 'Beauty & Cosmetics', 'Pure Botanics',
            'Rich in Vitamin E and essential fatty acids. Nourishes dry hair, tames frizz, and leaves skin supple and luminous.',
            'চুল পড়া রোধ, সিল্কি ভাব ফেরানো এবং ত্বকের উজ্জ্বলতা বৃদ্ধিতে খাঁটি মরোক্কান আরগান তেলের জাদুকরী কার্যকারিতা।',
            1200.0, 950.0, 20, 'BEA-ARG-100',
            'https://images.unsplash.com/photo-1608248597359-598687707e78?w=800&auto=format&fit=crop&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1608248597359-598687707e78?w=800&auto=format&fit=crop&q=80'
            ]),
            json.dumps(['Natural Gold']),
            json.dumps(['100ml']),
            0, 0, 4.8, 34
        ),

        # Home & Living
        (
            'Miyako 6-Litre Multi-Function Electric Pressure Cooker',
            'মিয়াকো ৬ লিটার মাল্টি-ফাংশন ইলেকট্রিক প্রেশার কুকার',
            'miyako-6l-electric-pressure-cooker',
            5, 'Home & Living', 'Miyako',
            'Smart 12-in-1 auto-cooking programs for meat, khichuri, soup, stew, and cake. Non-stick ceramic pot with 10 safety locks.',
            'স্বয়ংক্রিয় ১২টি রান্নার মোডসহ আধুনিক ইলেকট্রিক কুকার। গ্যাস ছাড়াই দ্রুত মাংস, বিরিয়ানি ও খিচুড়ি রাঁধুন স্বাস্থ্যকরভাবে।',
            6500.0, 5200.0, 14, 'HOM-MYK-6L',
            'https://images.unsplash.com/photo-1544233726-9f1d2b27be8b?w=800&auto=format&fit=crop&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1544233726-9f1d2b27be8b?w=800&auto=format&fit=crop&q=80'
            ]),
            json.dumps(['Metallic Silver', 'Obsidian Black']),
            json.dumps(['6 Litres']),
            1, 0, 4.9, 45
        ),
        (
            'Premium 100% Cotton King Size Bed Sheet with 2 Pillow Covers',
            'প্রিমিয়াম ১০০% সুতি কিং সাইজ বেডশিট সাথে ২টি বালিশের কভার',
            'cotton-king-size-bed-sheet-set',
            5, 'Home & Living', 'HomeComforts',
            'High 300-thread count breathable woven cotton with fade-proof vibrant geometric prints. Shrink resistant and machine washable.',
            '১০০% খাঁটি পাকা সুতি কাপড়ে তৈরি কিং সাইজ (৭.৫x৮ ফুট) আরামদায়ক বেডশিট। রঙ ওঠার ভয় নেই, ধোওয়া সহজ।',
            1850.0, 1450.0, 25, 'HOM-BED-300',
            'https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=800&auto=format&fit=crop&q=80',
            json.dumps([
                'https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=800&auto=format&fit=crop&q=80'
            ]),
            json.dumps(['Royal Blue Floral', 'Pastel Mint', 'Abstract Geometric']),
            json.dumps(['King Size (90x100 inch)']),
            0, 1, 4.6, 28
        )
    ]

    for p in products:
        cursor.execute('''
        INSERT INTO products (
            title, title_bn, slug, category_id, category_name, brand,
            description, description_bn, price, sale_price, stock, sku,
            image, gallery, colors, sizes, is_featured, is_flash_sale, rating, review_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', p)

    # 4. Seed Reviews
    reviews = [
        (1, 2, 'তানভীর হোসেন', 5, 'পাঞ্জাবির কোয়ালিটি ও কাজের ফিনিশিং অসাধারণ! ঠিক আড়ংয়ের মতোই গর্জিয়াস। দ্রুত ডেলিভারি পেয়েছি।', None, 5, 1),
        (1, 1, 'ফারহান আহমেদ', 5, 'Color match is 100% accurate. Fits perfectly on size L. Loved the bKash payment process!', None, 3, 1),
        (5, 2, 'আরিফুল ইসলাম', 5, 'ওয়ালটন টিভির পিকচার কোয়ালিটি ও সাউন্ড খুবই নিখুঁত। ৪কে ভিডিওতে দারুণ ব্রাইটনেস পাই।', None, 12, 1),
        (9, 2, 'নাজনীন সুলতানা', 5, 'খাঁটি সুন্দরবনের মধুর ঝাঁঝ আর গন্ধটা একদম বাস্তব। বোতলজাতকরণ খুব হাইজিনিক ছিল।', None, 7, 1),
        (10, 1, 'সাদমান জামান', 5, 'তেলের ঝাঁঝালো ঘ্রাণ আর স্বাদ চমৎকার। ইলিশ মাছ ভাজায় ট্রাই করেছি, অরিজিনাল টেস্ট পেয়েছি।', None, 4, 1),
        (6, 2, 'রাকিবুল হাসান', 5, 'স্যামসাং এ৫৫ এর ডিসপ্লে আর ব্যাটারি ব্যাকআপ দারুণ। একদিনের মধ্যেই ডেলিভারি পাইছি ঢাকায়।', None, 8, 1)
    ]

    for r in reviews:
        cursor.execute('''
        INSERT INTO reviews (product_id, user_id, user_name, rating, comment, image_url, helpful_count, verified_purchase)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', r)

    # 5. Seed Coupons
    now = datetime.now()
    exp_date = (now + timedelta(days=90)).strftime('%Y-%m-%d')
    coupons = [
        ('EID20', 'percentage', 20.0, 1500.0, 500.0, exp_date, 500, 24, 1),
        ('BONGO100', 'fixed', 100.0, 800.0, 100.0, exp_date, 1000, 86, 1),
        ('FREESHIP', 'fixed', 60.0, 1200.0, 60.0, exp_date, 200, 45, 1),
        ('WELCOME50', 'fixed', 50.0, 500.0, 50.0, exp_date, 300, 15, 1)
    ]

    for c in coupons:
        cursor.execute('''
        INSERT INTO coupons (code, discount_type, discount_value, min_spend, max_discount, expiry_date, usage_limit, used_count, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', c)

    # 6. Seed Sample Orders with varied statuses for admin analytics & live tracking demo
    past_date1 = (now - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
    past_date2 = (now - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    today_date = now.strftime('%Y-%m-%d %H:%M:%S')

    sample_orders = [
        (
            'BB-202611-1001', 2, 'তানভীর হোসেন', 'customer@bongobazaar.com', '01819000002',
            'হাউজ ১৫, রোড ৭, সেক্টর ৪, উত্তরা', 'Dhaka', 'Uttara', 'Standard',
            'bKash', 'Paid', 'BKASH98765432',
            3600.0, 0.0, 60.0, 3660.0, None, 'Delivered',
            'কাস্টমারকে কল করে ডেলিভারি দেওয়া হয়েছে', past_date1, past_date1
        ),
        (
            'BB-202611-1002', 2, 'তানভীর হোসেন', 'customer@bongobazaar.com', '01819000002',
            'ফ্ল্যাট ৪বি, ব্লক সি, বনানী', 'Dhaka', 'Banani', 'Express',
            'Nagad', 'Paid', 'NAGAD12345678',
            4290.0, 100.0, 120.0, 4310.0, 'BONGO100', 'Shipped',
            'কুরিয়ার পার্টনার রেডেক্স ট্র্যাকিং নং: RDX-98214', past_date2, past_date2
        ),
        (
            'BB-202611-1003', None, 'মাহবুব আলম', 'mahbub.alam@gmail.com', '01712345678',
            'গ্রাম: কাশিমপুর, পোস্ট: চান্দগাঁও', 'Chittagong', 'Chandgaon', 'Standard',
            'COD', 'Pending', None,
            1750.0, 0.0, 120.0, 1870.0, None, 'Processing',
            'পণ্য প্যাকিং চলছে ও চালানের প্রস্তুতি নেওয়া হচ্ছে', today_date, today_date
        ),
        (
            'BB-202611-1004', None, 'রুবাইয়া আক্তার', 'rubaiya@yahoo.com', '01987654321',
            'হাউজ ২১, লেক রোড, গুলশান-২', 'Dhaka', 'Gulshan', 'Express',
            'bKash', 'Paid', 'BKASH45127890',
            5200.0, 500.0, 60.0, 4760.0, 'EID20', 'Pending',
            'নতুন অর্ডার রিসিভ করা হয়েছে', today_date, today_date
        )
    ]

    for o in sample_orders:
        cursor.execute('''
        INSERT INTO orders (
            order_number, user_id, customer_name, customer_email, customer_phone,
            shipping_address, shipping_district, shipping_thana, delivery_type,
            payment_method, payment_status, transaction_id,
            subtotal, discount, shipping_fee, total_amount, coupon_code, order_status,
            notes, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', o)

    # Order items for order 1
    cursor.execute('''
    INSERT INTO order_items (order_id, product_id, product_title, price, quantity, color, size, image, total)
    VALUES (1, 1, 'Aarong Style Premium Silk Embroidered Panjabi', 3600.0, 1, 'Navy Blue', 'L (40)', 'https://images.unsplash.com/photo-1617127365659-c47fa864d8bc?w=800&auto=format&fit=crop&q=80', 3600.0)
    ''')

    # Order items for order 2
    cursor.execute('''
    INSERT INTO order_items (order_id, product_id, product_title, price, quantity, color, size, image, total)
    VALUES (2, 7, 'Realme Buds Air 6 Pro Wireless ANC Earbuds', 4290.0, 1, 'Titanium Silver', 'Standard', 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop&q=80', 4290.0)
    ''')

    # Order items for order 3
    cursor.execute('''
    INSERT INTO order_items (order_id, product_id, product_title, price, quantity, color, size, image, total)
    VALUES (3, 2, 'Traditional Tangail Soft Cotton Handloom Saree', 1750.0, 1, 'Mustard Yellow', 'Free Size (12 Haat)', 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&auto=format&fit=crop&q=80', 1750.0)
    ''')

    # Order items for order 4
    cursor.execute('''
    INSERT INTO order_items (order_id, product_id, product_title, price, quantity, color, size, image, total)
    VALUES (4, 12, 'Miyako 6-Litre Multi-Function Electric Pressure Cooker', 5200.0, 1, 'Metallic Silver', '6 Litres', 'https://images.unsplash.com/photo-1544233726-9f1d2b27be8b?w=800&auto=format&fit=crop&q=80', 5200.0)
    ''')

    conn.commit()
    conn.close()
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    init_db()
    seed_db()
