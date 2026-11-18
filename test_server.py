#!/usr/bin/env python3
"""
Automated Integration Test Suite for Katindhi Valley General Store Web Server
"""

import urllib.request
import urllib.parse
import json
import threading
import time
import sys
import os

# Ensure local directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import server
import database

PORT = 8899

def run_server():
    server.run(PORT)

def main():
    print("Initializing test server...")
    database.init_db()
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(1)

    base = f"http://127.0.0.1:{PORT}"
    print(f"Connecting to {base}...")

    # 1. Test GET /
    print("\n1. Testing GET / (Storefront):")
    with urllib.request.urlopen(f"{base}/") as res:
        assert res.status == 200
        content = res.read().decode('utf-8')
        assert "Katindhi Valley General Store" in content
        assert "Hitesh Gupta" in content
        assert "9418301840" in content
        assert "8:00 AM - 5:00 PM" in content
        print("  ✓ Storefront loaded successfully with all required details.")

    # 2. Test GET /admin
    print("\n2. Testing GET /admin (Owner Portal):")
    with urllib.request.urlopen(f"{base}/admin") as res:
        assert res.status == 200
        content = res.read().decode('utf-8')
        assert "Owner Portal" in content
        assert "Hitesh Gupta" in content
        print("  ✓ Owner Portal loaded successfully.")

    # 3. Test Static Assets
    print("\n3. Testing Static Assets:")
    with urllib.request.urlopen(f"{base}/static/css/style.css") as res:
        assert res.status == 200
        print("  ✓ CSS stylesheet served correctly.")
    with urllib.request.urlopen(f"{base}/static/js/app.js") as res:
        assert res.status == 200
        print("  ✓ JS app controller served correctly.")

    # 4. Test Store Info API
    print("\n4. Testing GET /api/store-info:")
    with urllib.request.urlopen(f"{base}/api/store-info") as res:
        data = json.loads(res.read().decode('utf-8'))
        assert data["success"] is True
        info = data["data"]
        assert info["owner"] == "Hitesh Gupta"
        assert info["phone"] == "9418301840"
        assert "8:00 AM" in info["timings"]
        assert "5:00 PM" in info["timings"]
        assert "operating_days" in info
        print(f"  ✓ Store Info API: {info['store_name']} | Status: {info['status_text']}")

    # 5. Test Categories API
    print("\n5. Testing GET /api/categories:")
    with urllib.request.urlopen(f"{base}/api/categories") as res:
        data = json.loads(res.read().decode('utf-8'))
        assert data["success"] is True
        assert len(data["categories"]) > 0
        cat_names = [c["name"] for c in data["categories"]]
        print(f"  ✓ Found {len(data['categories'])} categories: {', '.join(cat_names[:4])}...")

    # 6. Test Products API
    print("\n6. Testing GET /api/products:")
    with urllib.request.urlopen(f"{base}/api/products") as res:
        data = json.loads(res.read().decode('utf-8'))
        assert data["success"] is True
        assert data["count"] >= 40
        p0 = data["products"][0]
        print(f"  ✓ Catalog returned {data['count']} wholesale products. Sample: {p0['name']} ({p0['packaging']}) at ₹{p0['wholesale_price']}")

    # 7. Test Product Filtering & Search
    print("\n7. Testing Filtering & Search:")
    url = f"{base}/api/products?search=" + urllib.parse.quote("Atta")
    with urllib.request.urlopen(url) as res:
        data = json.loads(res.read().decode('utf-8'))
        assert data["success"] is True
        assert data["count"] > 0
        print(f"  ✓ Search for 'Atta' returned {data['count']} matching products.")

    # 8. Test Order Placement
    print("\n8. Testing POST /api/orders (Wholesale Order Placement):")
    order_data = {
        "customer_name": "Ramesh Kumar",
        "shop_name": "Kumar Tea Stall & Bakery",
        "phone": "9876543210",
        "address": "Lower Bazar, Katindhi Valley",
        "delivery_type": "Delivery",
        "delivery_slot": "Morning (8:00 AM - 1:00 PM)",
        "payment_method": "Cash on Delivery",
        "notes": "Deliver by 10 AM please",
        "items": [
            {
                "id": 1,
                "name": "Sharbati Whole Wheat Atta",
                "packaging": "50 kg Bag",
                "wholesale_price": 1750.0,
                "price": 1750.0,
                "qty": 2
            },
            {
                "id": 19,
                "name": "Kachi Ghani Pure Mustard Oil",
                "packaging": "15 Litre Tin",
                "wholesale_price": 2050.0,
                "price": 2050.0,
                "qty": 1
            }
        ],
        "subtotal": 5550.0,
        "discount": 0.0,
        "total_amount": 5550.0
    }

    req = urllib.request.Request(
        f"{base}/api/orders",
        data=json.dumps(order_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as res:
        assert res.status == 201
        data = json.loads(res.read().decode('utf-8'))
        assert data["success"] is True
        order_info = data["data"]
        order_no = order_info["order_number"]
        whatsapp_url = order_info["whatsapp_url"]
        assert "9418301840" in whatsapp_url
        print(f"  ✓ Placed Order: {order_no} | Total: ₹{order_info['total_amount']}")
        print(f"  ✓ WhatsApp Link created pointing to Hitesh Gupta (+91 9418301840)")

    # 9. Test Order Lookup
    print("\n9. Testing GET /api/orders/<order_number>:")
    with urllib.request.urlopen(f"{base}/api/orders/{order_no}") as res:
        data = json.loads(res.read().decode('utf-8'))
        assert data["success"] is True
        fetched = data["order"]
        assert fetched["order_number"] == order_no
        assert fetched["customer_name"] == "Ramesh Kumar"
        assert fetched["total_amount"] == 5550.0
        assert len(fetched["items"]) == 2
        print(f"  ✓ Successfully verified order in DB. Status: {fetched['status']}")

    # 10. Test Status Update
    print("\n10. Testing POST /api/orders/update-status:")
    update_req = urllib.request.Request(
        f"{base}/api/orders/update-status",
        data=json.dumps({"order_id": order_no, "status": "Confirmed"}).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(update_req) as res:
        assert res.status == 200
        data = json.loads(res.read().decode('utf-8'))
        assert data["success"] is True
        print("  ✓ Order status updated to Confirmed.")

    # 11. Test Admin Stats
    print("\n11. Testing GET /api/stats:")
    with urllib.request.urlopen(f"{base}/api/stats") as res:
        data = json.loads(res.read().decode('utf-8'))
        assert data["success"] is True
        stats = data["stats"]
        assert stats["total_orders"] >= 1
        assert stats["total_sales"] >= 5550.0
        print(f"  ✓ Admin Stats: Orders={stats['total_orders']}, Sales=₹{stats['total_sales']}")

    print("\n========================================================")
    print(" ALL 11 TEST SUITES PASSED FLAWLESSLY! 🚀")
    print("========================================================")

if __name__ == "__main__":
    main()
