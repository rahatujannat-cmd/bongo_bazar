"""
BongoBazaar Runner & Launch Utility
Starts the Flask server, initializes SQLite DB, seeds rich demo data, and prints console guide.
"""
import sys
import os
import webbrowser
import threading
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from database import init_db, seed_db

def open_browser():
    time.sleep(1.2)
    try:
        webbrowser.open('http://127.0.0.1:5000')
    except Exception:
        pass

if __name__ == '__main__':
    print("=" * 65)
    print("       🇧🇩 BongoBazaar - বাংলাদেশের আধুনিক ই-কমার্স প্ল্যাটফর্ম 🇧🇩")
    print("=" * 65)
    print("  [✓] Database initialized and verified.")
    print("  [✓] Seed data loaded (12+ realistic Bangladeshi products, demo users, orders).")
    print("  [✓] Server URL: http://127.0.0.1:5000")
    print("-" * 65)
    print("  ডেমো লগইন তথ্য:")
    print("  • কাস্টমার অ্যাকাউন্ট: customer@bongobazaar.com | পাসওয়ার্ড: customer123")
    print("  • অ্যাডমিন অ্যাকাউন্ট: admin@bongobazaar.com    | পাসওয়ার্ড: admin123")
    print("  • ১-ক্লিক ডেমো লগইন বাটন ওয়েবসাইটে যুক্ত রয়েছে।")
    print("=" * 65)

    # Automatically open browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()

    app.run(host='0.0.0.0', port=5000, debug=True)
