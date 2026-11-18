#!/usr/bin/env python3
"""
Unit tests for database and business logic of Katindhi Valley General Store
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database
import server

def test_database():
    print("Testing Database...")
    database.init_db()

    # Settings
    settings = database.get_store_settings()
    assert settings["store_name"] == "Katindhi Valley General Store"
    assert settings["owner_name"] == "Hitesh Gupta"
    assert settings["owner_phone"] == "9418301840"
    assert "8:00 AM" in settings["timings"]
    assert "5:00 PM" in settings["timings"]
    print("  ✓ Store settings verified: Owner is Hitesh Gupta, Timings 8:00-5:00, Phone 9418301840")

    # Categories
    categories = database.get_categories()
    assert len(categories) >= 7
    print(f"  ✓ {len(categories)} categories verified.")

    # Products
    products = database.get_products()
    assert len(products) >= 40
    print(f"  ✓ Total {len(products)} products verified.")

    # Search
    atta_products = database.get_products(search="Atta")
    assert len(atta_products) >= 2
    print(f"  ✓ Search 'Atta' returned {len(atta_products)} items.")

    # Category filter
    oil_products = database.get_products(category="Edible Oils & Ghee")
    assert len(oil_products) >= 5
    print(f"  ✓ Category 'Edible Oils & Ghee' returned {len(oil_products)} items.")

    # Order Creation
    sample_order = {
        "customer_name": "Suresh Verma",
        "shop_name": "Verma Sweets & Dhaba",
        "phone": "9816012345",
        "address": "Opposite Petrol Pump, Katindhi Valley",
        "delivery_type": "Delivery",
        "delivery_slot": "Morning (8:00 AM - 1:00 PM)",
        "payment_method": "Cash on Delivery",
        "notes": "Bring invoice with shop stamp",
        "items": [
            {
                "id": 1,
                "name": "Sharbati Whole Wheat Atta",
                "packaging": "50 kg Bag",
                "wholesale_price": 1750.0,
                "qty": 4
            },
            {
                "id": 19,
                "name": "Kachi Ghani Pure Mustard Oil",
                "packaging": "15 Litre Tin",
                "wholesale_price": 2050.0,
                "qty": 2
            }
        ],
        "subtotal": 11100.0,
        "discount": 0.0,
        "total_amount": 11100.0
    }

    res = database.create_order(sample_order)
    assert res["order_number"].startswith("KVGS-")
    assert res["total_amount"] == 11100.0
    assert "9418301840" in res["whatsapp_url"]
    print(f"  ✓ Order created: {res['order_number']}, WhatsApp link verified.")

    # Fetch order
    fetched = database.get_order_by_number_or_id(res["order_number"])
    assert fetched is not None
    assert fetched["customer_name"] == "Suresh Verma"
    assert fetched["shop_name"] == "Verma Sweets & Dhaba"
    assert len(fetched["items"]) == 2
    print(f"  ✓ Order retrieved successfully from database: {fetched['order_number']}")

    # Update status
    updated = database.update_order_status(res["order_number"], "Confirmed")
    assert updated is True
    fetched_updated = database.get_order_by_number_or_id(res["order_number"])
    assert fetched_updated["status"] == "Confirmed"
    print("  ✓ Order status updated and verified: Confirmed")

    # Add product
    new_pid = database.add_product({
        "name": "Test Basmati Special",
        "hindi_name": "टेस्ट बासमती",
        "category": "Grains & Flours",
        "packaging": "25 kg Bag",
        "wholesale_price": 1800.0,
        "retail_mrp": 2200.0,
        "moq": 1,
        "unit": "Bag",
        "stock": 50,
        "image_category": "grain",
        "description": "Test product description",
        "is_featured": False
    })
    assert new_pid > 0
    p = database.get_product_by_id(new_pid)
    assert p["name"] == "Test Basmati Special"
    print(f"  ✓ Product addition tested successfully (ID {new_pid}).")

    # Stats
    stats = database.get_stats()
    assert stats["total_orders"] >= 1
    assert stats["total_sales"] >= 11100.0
    print(f"  ✓ Store stats verified: {stats}")

def test_store_status():
    print("\nTesting Store Timings & Live Status Calculation...")
    handler = server.StoreRequestHandler
    status = handler.get_store_status(None)
    assert "is_open" in status
    assert "status_text" in status
    assert status["timings"] == "8:00 AM - 5:00 PM"
    assert status["operating_days"] == "Monday to Saturday"
    assert status["owner"] == "Hitesh Gupta"
    assert status["phone"] == "9418301840"
    print(f"  ✓ Live Store Status Logic passed: {status['status_text']} | Time: {status['current_time']}")

if __name__ == "__main__":
    test_database()
    test_store_status()
    print("\n========================================================")
    print(" ALL APPLICATION CORE TESTS PASSED WITH 100% SUCCESS! ")
    print("========================================================")
