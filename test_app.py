"""
BongoBazaar Comprehensive Test Suite
Tests page routing, REST APIs, cart, coupon validation, checkout, order tracking, and admin endpoints.
"""
import unittest
import json
from app import app
from database import get_db, init_db, seed_db

class BongoBazaarTestSuite(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_01_home_page(self):
        res = self.app.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Bongo', res.data)
        self.assertIn(b'Bazaar', res.data)
        print("✓ Home page loaded successfully")

    def test_02_shop_page(self):
        res = self.app.get('/shop')
        self.assertEqual(res.status_code, 200)
        print("✓ Shop page loaded successfully")

    def test_03_products_api(self):
        res = self.app.get('/api/products')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertGreater(data['count'], 0)
        print(f"✓ Products API returned {data['count']} items")

    def test_04_categories_api(self):
        res = self.app.get('/api/categories')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['categories']), 0)
        print(f"✓ Categories API returned {len(data['categories'])} categories")

    def test_05_single_product_detail_page(self):
        res = self.app.get('/product/1')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Panjabi', res.data)
        print("✓ Product detail page rendered correctly")

    def test_06_coupon_validation(self):
        # Valid coupon
        res = self.app.post('/api/coupons/validate', json={'code': 'EID20', 'subtotal': 2000})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['discount'], 400.0)

        # Minimum spend requirement error check
        res2 = self.app.post('/api/coupons/validate', json={'code': 'EID20', 'subtotal': 500})
        self.assertEqual(res2.status_code, 400)
        print("✓ Coupon validation engine functioning accurately")

    def test_07_order_creation_and_checkout(self):
        order_payload = {
            'customer_name': 'সাকিব আল হাসান',
            'customer_phone': '01712345678',
            'customer_email': 'shakib@test.com',
            'shipping_district': 'Dhaka',
            'shipping_thana': 'Gulshan',
            'shipping_address': 'Road 11, Block D, Gulshan-2',
            'delivery_type': 'Standard',
            'payment_method': 'bKash',
            'transaction_id': 'BKASH992812',
            'coupon_code': 'BONGO100',
            'items': [
                {
                    'id': 1,
                    'title': 'Aarong Style Premium Silk Embroidered Panjabi',
                    'price': 3600.0,
                    'quantity': 1,
                    'color': 'Navy Blue',
                    'size': 'L (40)',
                    'image': 'https://images.unsplash.com/photo-1617127365659-c47fa864d8bc?w=800'
                }
            ]
        }
        res = self.app.post('/api/orders/create', json=order_payload)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertTrue(data['order_number'].startswith('BB-'))
        order_no = data['order_number']
        print(f"✓ Order created successfully with number: {order_no}")

        # Test Order Tracking for the new order
        res_track = self.app.get(f'/api/orders/track/{order_no}')
        self.assertEqual(res_track.status_code, 200)
        track_data = json.loads(res_track.data)
        self.assertTrue(track_data['success'])
        self.assertEqual(track_data['order']['order_number'], order_no)
        print(f"✓ Order tracking endpoint verified for {order_no}")

    def test_08_order_tracking_existing_seed(self):
        res = self.app.get('/api/orders/track/BB-202611-1001')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['order']['order_status'], 'Delivered')
        print("✓ Pre-seeded order tracking verified")

    def test_09_customer_demo_login_and_account(self):
        res = self.app.post('/api/auth/demo-login', json={'role': 'customer'})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['role'], 'customer')

        # Access Account page
        res_acc = self.app.get('/account')
        self.assertEqual(res_acc.status_code, 200)
        print("✓ Customer demo authentication and profile verified")

    def test_10_admin_demo_login_and_dashboard(self):
        res = self.app.post('/api/auth/demo-login', json={'role': 'admin'})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['role'], 'admin')

        # Access Admin Dashboard & Stats
        res_admin = self.app.get('/admin')
        self.assertEqual(res_admin.status_code, 200)

        res_stats = self.app.get('/api/admin/stats')
        self.assertEqual(res_stats.status_code, 200)
        stats_data = json.loads(res_stats.data)
        self.assertTrue(stats_data['success'])
        self.assertGreater(stats_data['stats']['total_sales'], 0)
        print(f"✓ Admin dashboard analytics verified (Sales: ৳{stats_data['stats']['total_sales']})")

    def test_11_essential_pages(self):
        pages = ['/about', '/contact', '/terms', '/returns', '/privacy', '/cart', '/checkout', '/wishlist', '/track']
        for p in pages:
            res = self.app.get(p)
            self.assertEqual(res.status_code, 200, f"Page {p} returned status {res.status_code}")
        print("✓ All essential pages (/about, /contact, /terms, /returns, /privacy, etc.) verified (200 OK)")

    def test_12_printable_invoice(self):
        res = self.app.get('/admin/invoice/BB-202611-1001')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'INVOICE', res.data)
        print("✓ Printable invoice rendered correctly")

if __name__ == '__main__':
    unittest.main()
