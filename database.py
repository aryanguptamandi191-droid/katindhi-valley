"""
Database management for Katindhi Valley General Store
Wholesale Grocery Store - Owner: Hitesh Gupta (9418301840)
"""

import sqlite3
import os
import json
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "store.db")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        hindi_name TEXT,
        category TEXT NOT NULL,
        packaging TEXT NOT NULL,
        wholesale_price REAL NOT NULL,
        retail_mrp REAL NOT NULL,
        moq INTEGER DEFAULT 1,
        unit TEXT DEFAULT 'Pack',
        stock INTEGER DEFAULT 100,
        image_category TEXT DEFAULT 'grain',
        description TEXT,
        is_featured INTEGER DEFAULT 0
    )
    """)

    # Create orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE NOT NULL,
        customer_name TEXT NOT NULL,
        shop_name TEXT,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        delivery_type TEXT DEFAULT 'Delivery',
        delivery_slot TEXT,
        payment_method TEXT DEFAULT 'Cash on Delivery',
        notes TEXT,
        items_json TEXT NOT NULL,
        subtotal REAL NOT NULL,
        discount REAL DEFAULT 0,
        total_amount REAL NOT NULL,
        status TEXT DEFAULT 'Pending',
        created_at TEXT NOT NULL
    )
    """)

    # Create store_settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS store_settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # Seed default settings
    default_settings = {
        "store_name": "Katindhi Valley General Store",
        "hindi_name": "कटिंढी वैली जनरल स्टोर",
        "tagline": "Wholesale Grocery & Bulk Provisions",
        "owner_name": "Hitesh Gupta",
        "owner_phone": "9418301840",
        "timings": "8:00 AM - 5:00 PM",
        "operating_days": "Monday to Saturday",
        "sunday_status": "Closed (Orders accepted online)",
        "address": "Main Market, Katindhi Valley, Himachal Pradesh",
        "min_wholesale_order": "1500",
        "notice": "All groceries available in bulk bags, tins & cartons at wholesale mandi rates."
    }

    for key, val in default_settings.items():
        cursor.execute("INSERT OR IGNORE INTO store_settings (key, value) VALUES (?, ?)", (key, val))

    # Check if products need seeding
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]

    if count == 0:
        seed_products(cursor)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def seed_products(cursor):
    sample_products = [
        # Grains & Flours
        ("Sharbati Whole Wheat Atta", "शरबती चक्की आटा", "Grains & Flours", "50 kg Bag", 1750.0, 2100.0, 1, "Bag", 120, "grain", "Premium MP Sharbati wheat flour, stone ground fresh for soft rotis. Best wholesale rate for bakeries and retailers.", 1),
        ("Sharbati Whole Wheat Atta", "शरबती चक्की आटा", "Grains & Flours", "25 kg Bag", 900.0, 1080.0, 1, "Bag", 150, "grain", "High protein pure whole wheat chakki fresh atta in strong woven pack.", 1),
        ("Fine Maida (All Purpose Flour)", "प्रीमियम मैदा", "Grains & Flours", "50 kg Bag", 1600.0, 1950.0, 1, "Bag", 80, "grain", "Refined fine grade maida for sweets, halwais, restaurants, and local general stores.", 0),
        ("Sooji / Rawa (Fine Semolina)", "सूजी / रवा", "Grains & Flours", "50 kg Bag", 1700.0, 2050.0, 1, "Bag", 70, "grain", "Crisp golden semolina for halwa, snacks, and bulk kitchen use.", 0),
        ("Classic Basmati Rice (XXL Grain)", "क्लासिक बासमती चावल", "Grains & Flours", "30 kg Bag", 2850.0, 3600.0, 1, "Bag", 95, "grain", "Aromatic aged long grain basmati rice. Cook length doubles, perfect for functions and retail resale.", 1),
        ("Sella / Parboiled Golden Rice", "गोल्डन सेला चावल", "Grains & Flours", "50 kg Bag", 2400.0, 2950.0, 1, "Bag", 110, "grain", "Non-sticky durable grain sella rice, widely preferred for catering and daily meals.", 0),
        ("Daily Kolam Rice (Pona / Tukda)", "डेली कोलम चावल", "Grains & Flours", "50 kg Bag", 1950.0, 2400.0, 1, "Bag", 85, "grain", "High quality daily use polished rice bag for family consumption and retail.", 0),
        ("Makki Ka Atta (Yellow Maize Flour)", "पीला मक्की का आटा", "Grains & Flours", "25 kg Bag", 780.0, 950.0, 1, "Bag", 60, "grain", "Fresh ground Himachal yellow maize flour for authentic valley rotis.", 1),
        ("Thick Poha (Flattened Rice)", "मोटा पोहा", "Grains & Flours", "30 kg Bag", 1250.0, 1550.0, 1, "Bag", 50, "grain", "Cleaned sorted white flattened rice for breakfast snacks.", 0),

        # Pulses & Dals
        ("Desi Toor / Arhar Dal (Fatka)", "देसी तुअर / अरहर दाल", "Pulses & Dals", "30 kg Bag", 4350.0, 5100.0, 1, "Bag", 80, "pulse", "Unpolished unadulterated high grade fatka toor dal with quick cooking time.", 1),
        ("Moong Dal Dhuli (Yellow)", "मूंग दाल धुली", "Pulses & Dals", "30 kg Bag", 3450.0, 4050.0, 1, "Bag", 75, "pulse", "Finely sorted yellow split moong dal, easy to digest and rich in protein.", 0),
        ("Chana Dal (Special Mandi Grade)", "चना दाल स्पेशल", "Pulses & Dals", "30 kg Bag", 2600.0, 3100.0, 1, "Bag", 90, "pulse", "Bright golden bold chana dal for besan making, sweets, and savoury snacks.", 1),
        ("Himachali Chitra Rajma (Red Kidney Beans)", "चित्रा राजमा", "Pulses & Dals", "25 kg Bag", 3300.0, 4000.0, 1, "Bag", 85, "pulse", "Authentic soft cooking speckled valley rajma. Highly demanded in local hill markets.", 1),
        ("Kabuli Chana (Dollar Bold 12mm)", "काबुली चना (डॉलर)", "Pulses & Dals", "30 kg Bag", 3900.0, 4800.0, 1, "Bag", 65, "pulse", "Jumbo size white chickpeas, cooks tender and large. Premium restaurant standard.", 1),
        ("Kala Chana (Desi Black Gram)", "देसी काला चना", "Pulses & Dals", "30 kg Bag", 2350.0, 2800.0, 1, "Bag", 70, "pulse", "Iron-rich clean brown chickpeas for sprouts and traditional curry.", 0),
        ("Urad Sabut (Whole Black Matpe)", "उड़द साबुत काली दाल", "Pulses & Dals", "30 kg Bag", 3450.0, 4200.0, 1, "Bag", 60, "pulse", "High quality black gram for famous Dal Makhani and Pahadi preparations.", 0),
        ("Masoor Malka (Red Lentils)", "मलका मसूर दाल", "Pulses & Dals", "30 kg Bag", 2550.0, 3150.0, 1, "Bag", 75, "pulse", "Evenly split pink lentils, quick boiling with high protein content.", 0),

        # Edible Oils & Ghee
        ("Kachi Ghani Pure Mustard Oil", "कच्ची घानी सरसों का तेल", "Edible Oils & Ghee", "15 Litre Tin", 2050.0, 2450.0, 1, "Tin", 140, "oil", "Strong pungency traditional cold-pressed mustard oil in heavy gauge sealed tin.", 1),
        ("Refined Soyabean Oil", "रिफाइंड सोयाबीन तेल", "Edible Oils & Ghee", "15 Litre Tin", 1750.0, 2100.0, 1, "Tin", 120, "oil", "Light healthy cooking oil, zero cholesterol, ideal for frying and snacks.", 1),
        ("Fortune Kachi Ghani 1L Pouches", "फॉर्च्यून सरसों तेल पाउच", "Edible Oils & Ghee", "Carton (16 Pouches x 1L)", 2320.0, 2640.0, 1, "Carton", 60, "oil", "Branded premium mustard oil pouches in original company carton packaging.", 1),
        ("Refined Sunflower Oil 1L Pouches", "सनफ्लावर तेल पाउच", "Edible Oils & Ghee", "Carton (15 Pouches x 1L)", 1980.0, 2350.0, 1, "Carton", 50, "oil", "Crystal clear sunflower oil in retail ready box.", 0),
        ("Pure Desi Cow Ghee (Amarkot/Verka)", "शुद्ध देसी घी टिन", "Edible Oils & Ghee", "15 kg Tin", 8700.0, 10200.0, 1, "Tin", 35, "oil", "Granular aromatic pure cow ghee tin for ceremonies, sweet shops, and family stores.", 1),
        ("Pure Desi Ghee 1L Jars Box", "देसी घी 1 लीटर जार", "Edible Oils & Ghee", "Box (12 Jars x 1L)", 7100.0, 8160.0, 1, "Box", 40, "oil", "Convenient consumer retail 1-litre pet jars box for grocery shop counters.", 0),
        ("Vegetable Vanaspati Ghee", "वनस्पति घी टिन", "Edible Oils & Ghee", "15 Litre Tin", 1550.0, 1850.0, 1, "Tin", 50, "oil", "Commercial grade vanaspati for crispy frying, samosas, and namkeens.", 0),

        # Sugar, Jaggery & Salt
        ("M30 Refined Crystal Sugar", "सफेद चीनी (M-30)", "Sugar & Salt", "50 kg Bag", 2150.0, 2450.0, 1, "Bag", 180, "sugar", "Sparkling white sulphur-free standard M-30 sugar crystal bag.", 1),
        ("Pure Desi Gur / Jaggery (Laddoo)", "देसी गुड़ लड्डू", "Sugar & Salt", "10 kg Box", 520.0, 680.0, 1, "Box", 90, "sugar", "Natural unbleached sugarcane jaggery rounds, authentic winter valley staple.", 1),
        ("Tata Vacuum Salt (Iodized)", "टाटा नमक 1kg पैकेट", "Sugar & Salt", "Bag (25 Packets x 1kg)", 650.0, 750.0, 1, "Bag", 110, "sugar", "Original Tata iodized salt bags for retail distribution.", 1),
        ("Sendha Namak (Rock Salt Granules)", "सेंधा नमक (सफेद)", "Sugar & Salt", "25 kg Bag", 600.0, 800.0, 1, "Bag", 40, "sugar", "Pure Himalayan rock salt for fasting (vrat) and Ayurvedic health use.", 0),
        ("Kala Namak (Black Salt Lump)", "काला नमक साबुत", "Sugar & Salt", "25 kg Bag", 550.0, 750.0, 1, "Bag", 30, "sugar", "Authentic natural black salt rocks for spice blending and chatpata snacks.", 0),

        # Spices & Masala Wholesale
        ("Sabut Jeera / Cumin Seeds (Machine Clean)", "साबुत जीरा (मशीन क्लीन)", "Spices & Masala", "5 kg Pack", 1550.0, 1950.0, 1, "Pack", 65, "spice", "High oil aroma unadulterated Gujarat cumin seeds with negligible dust.", 1),
        ("Sabut Dhania / Coriander Seeds (Green)", "हरा साबुत धनिया", "Spices & Masala", "10 kg Bag", 1150.0, 1500.0, 1, "Bag", 50, "spice", "Fragrant dried whole coriander for grinding or direct cooking.", 0),
        ("Haldi Powder (Pure Salem Turmeric)", "हल्दी पाउडर (सेलम)", "Spices & Masala", "5 kg Pack", 980.0, 1300.0, 1, "Pack", 75, "spice", "Deep natural yellow curcumin-rich turmeric powder without artificial color.", 1),
        ("Teja Lal Mirch Powder (Spicy Red)", "तेजा लाल मिर्च पाउडर", "Spices & Masala", "5 kg Pack", 1250.0, 1650.0, 1, "Pack", 70, "spice", "Vibrant red color and sharp heat chilli powder for valley cooking.", 1),
        ("Whole Black Pepper (Tellicherry Garbled)", "काली मिर्च साबुत", "Spices & Masala", "2 kg Pack", 1450.0, 1850.0, 1, "Pack", 45, "spice", "Bold wrinkled pungent black peppercorns.", 0),
        ("Shahi Garam Masala Blend (Special)", "शाही गरम मसाला ब्लेंड", "Spices & Masala", "5 kg Bucket", 1850.0, 2400.0, 1, "Pack", 40, "spice", "Hand-roasted master spice mix containing cardamom, clove, mace, cinnamon, and bay leaf.", 1),
        ("Methi Dana (Fenugreek Seeds)", "मेथी दाना", "Spices & Masala", "5 kg Pack", 420.0, 580.0, 1, "Pack", 40, "spice", "Clean yellow bitter-sweet fenugreek seeds for pickles and curries.", 0),
        ("Kashmiri Deggi Mirch (Color & Mild)", "कश्मीरी देगी मिर्च", "Spices & Masala", "5 kg Pack", 1650.0, 2150.0, 1, "Pack", 55, "spice", "Imparts deep natural red gravies without overpowering heat.", 0),

        # Tea, Packaged & Provisions
        ("Assam CTC Leaf Tea (Gold Blend)", "असम कड़क चाय पत्ती", "Tea & Packaged", "5 kg Bulk Bag", 1450.0, 1900.0, 1, "Bag", 90, "tea", "Rich liquor strong aroma CTC tea blend specially suited for dhabas, tea stalls, and homes.", 1),
        ("Green Cardamom (Choti Elaichi 7.5mm)", "छोटी इलायची (हरी)", "Tea & Packaged", "1 kg Sealed Pouch", 2400.0, 2900.0, 1, "Pouch", 30, "tea", "Fresh green fragrant cardamom pods from Idukki.", 1),
        ("Maggi 2-Minute Noodles Carton", "मैगी नूडल्स कार्टन", "Tea & Packaged", "Carton (96 Packs x 70g)", 1250.0, 1440.0, 1, "Carton", 85, "tea", "Original Nestle Maggi wholesale carton for local store counters.", 1),
        ("Parle-G Glucose Biscuits Carton", "पारले-जी बिस्कुट कार्टन", "Tea & Packaged", "Carton (120 Packs)", 520.0, 600.0, 1, "Carton", 100, "tea", "Fastest moving tea-time biscuit carton with guaranteed wholesale margin.", 1),
        ("Roasted Namkeen Mixture Assorted", "मिक्स नमकीन क्रेट", "Tea & Packaged", "Carton (50 Packets)", 850.0, 1050.0, 1, "Carton", 60, "tea", "Crispy spiced aloo bhujia and mixture packets for quick counter resale.", 0),

        # Cleaning, Soap & Household
        ("Washing Powder (High Foam Detergent)", "डिटर्जेंट वाशिंग पाउडर", "Cleaning & Household", "50 kg Bulk Bag", 1950.0, 2600.0, 1, "Bag", 80, "cleaning", "Super whitening active formula powder for hotels, laundries, and village retail distribution.", 1),
        ("Detergent Cake / Laundry Bar", "कपड़े धोने का साबुन", "Cleaning & Household", "Carton (72 Bars)", 820.0, 1000.0, 1, "Carton", 70, "cleaning", "Heavy stain removing washing soap bars in convenient master carton.", 0),
        ("Dishwash Gel / Bar Wholesale Pack", "बर्तन धोने का साबुन बार", "Cleaning & Household", "Carton (96 Bars)", 890.0, 1100.0, 1, "Carton", 65, "cleaning", "Lemon fragrance anti-grease scrubbing bars with wholesale margins.", 0),
        ("Bath Soap (Assorted 100g Bars)", "नहाने का साबुन बॉक्स", "Cleaning & Household", "Carton (72 Bars)", 1350.0, 1650.0, 1, "Carton", 55, "cleaning", "Glycerine and neem herbal bathing soap box for general merchant shops.", 0),
        ("Concentrated White Phenyl", "सफेद फिनाइल (फ्लोर क्लीनर)", "Cleaning & Household", "5 Litre Can x 4 (Box)", 720.0, 960.0, 1, "Box", 50, "cleaning", "Pine fragrance disinfectant floor cleaner wholesale can pack.", 0),

        # Dry Fruits & Nuts
        ("California Almonds (Badam Giri)", "कैलिफ़ोर्निया बादाम गिरी", "Dry Fruits & Nuts", "10 kg Box", 7400.0, 9000.0, 1, "Box", 40, "dryfruit", "Sweet crunch uniform size California almonds for retail packaging and celebrations.", 1),
        ("Cashew Nuts W320 (Kaju Tukda/Sabut)", "काजू W-320 साबुत", "Dry Fruits & Nuts", "10 kg Tin", 7900.0, 9500.0, 1, "Tin", 35, "dryfruit", "First grade whole white cashews, perfect for festive gift boxes and confectionery.", 1),
        ("Golden Kishmish (Green Raisins)", "हरी किशमिश (दाख)", "Dry Fruits & Nuts", "10 kg Box", 2800.0, 3600.0, 1, "Box", 50, "dryfruit", "Plump sweet seedless green valley kishmish.", 1),
        ("Walnut Kernels (Akhrot Giri Pahadi)", "अखरोट गिरी (पहाड़ी)", "Dry Fruits & Nuts", "5 kg Box", 4600.0, 5800.0, 1, "Box", 40, "dryfruit", "Pure mountain walnut halves, rich in omega-3 and fresh natural oils.", 1),
    ]

    for p in sample_products:
        cursor.execute("""
        INSERT INTO products (
            name, hindi_name, category, packaging, wholesale_price, retail_mrp,
            moq, unit, stock, image_category, description, is_featured
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, p)

def get_store_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM store_settings")
    rows = cursor.fetchall()
    conn.close()
    return {row["key"]: row["value"] for row in rows}

def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM products 
        GROUP BY category 
        ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{"name": row["category"], "count": row["count"]} for row in rows]

def get_products(category=None, search=None, featured=None, sort=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if category and category.lower() != 'all':
        query += " AND category = ?"
        params.append(category)

    if featured:
        query += " AND is_featured = 1"

    if search:
        query += " AND (name LIKE ? OR hindi_name LIKE ? OR description LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])

    if sort == "price_asc":
        query += " ORDER BY wholesale_price ASC"
    elif sort == "price_desc":
        query += " ORDER BY wholesale_price DESC"
    elif sort == "name_asc":
        query += " ORDER BY name ASC"
    else:
        query += " ORDER BY is_featured DESC, id ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    products = []
    for row in rows:
        margin_percent = round(((row["retail_mrp"] - row["wholesale_price"]) / row["retail_mrp"]) * 100, 1) if row["retail_mrp"] > 0 else 0
        products.append({
            "id": row["id"],
            "name": row["name"],
            "hindi_name": row["hindi_name"],
            "category": row["category"],
            "packaging": row["packaging"],
            "wholesale_price": row["wholesale_price"],
            "retail_mrp": row["retail_mrp"],
            "savings": round(row["retail_mrp"] - row["wholesale_price"], 2),
            "margin_percent": margin_percent,
            "moq": row["moq"],
            "unit": row["unit"],
            "stock": row["stock"],
            "image_category": row["image_category"],
            "description": row["description"],
            "is_featured": bool(row["is_featured"])
        })
    return products

def get_product_by_id(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    margin_percent = round(((row["retail_mrp"] - row["wholesale_price"]) / row["retail_mrp"]) * 100, 1) if row["retail_mrp"] > 0 else 0
    return {
        "id": row["id"],
        "name": row["name"],
        "hindi_name": row["hindi_name"],
        "category": row["category"],
        "packaging": row["packaging"],
        "wholesale_price": row["wholesale_price"],
        "retail_mrp": row["retail_mrp"],
        "savings": round(row["retail_mrp"] - row["wholesale_price"], 2),
        "margin_percent": margin_percent,
        "moq": row["moq"],
        "unit": row["unit"],
        "stock": row["stock"],
        "image_category": row["image_category"],
        "description": row["description"],
        "is_featured": bool(row["is_featured"])
    }

def create_order(data):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Generate unique order number: KVGS-YYYYMMDD-XXXX
    now = datetime.now()
    cursor.execute("SELECT COUNT(*) FROM orders")
    order_seq = cursor.fetchone()[0] + 1
    order_number = f"KVGS-{now.strftime('%y%m%d')}-{order_seq:04d}"

    created_at = now.strftime("%Y-%m-%d %H:%M:%S")

    items = data.get("items", [])
    subtotal = float(data.get("subtotal", 0))
    discount = float(data.get("discount", 0))
    total_amount = float(data.get("total_amount", subtotal - discount))

    cursor.execute("""
    INSERT INTO orders (
        order_number, customer_name, shop_name, phone, address,
        delivery_type, delivery_slot, payment_method, notes,
        items_json, subtotal, discount, total_amount, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order_number,
        data.get("customer_name", "").strip(),
        data.get("shop_name", "").strip(),
        data.get("phone", "").strip(),
        data.get("address", "").strip(),
        data.get("delivery_type", "Delivery"),
        data.get("delivery_slot", "Morning (8:00 AM - 1:00 PM)"),
        data.get("payment_method", "Cash on Delivery"),
        data.get("notes", "").strip(),
        json.dumps(items),
        subtotal,
        discount,
        total_amount,
        "Pending",
        created_at
    ))

    conn.commit()
    order_id = cursor.lastrowid
    conn.close()

    # Build WhatsApp message link for owner Hitesh Gupta (+91 9418301840)
    store_owner_phone = "919418301840"
    wa_text = f"🛒 *NEW WHOLESALE ORDER - KATINDHI VALLEY STORE*\n"
    wa_text += f"━━━━━━━━━━━━━━━━━━━━\n"
    wa_text += f"📦 *Order ID:* {order_number}\n"
    wa_text += f"👤 *Customer:* {data.get('customer_name')}\n"
    if data.get('shop_name'):
        wa_text += f"🏢 *Shop/Business:* {data.get('shop_name')}\n"
    wa_text += f"📞 *Phone:* {data.get('phone')}\n"
    wa_text += f"📍 *Address:* {data.get('address')}\n"
    wa_text += f"🚚 *Mode:* {data.get('delivery_type', 'Delivery')} ({data.get('delivery_slot', 'Standard')})\n"
    wa_text += f"💳 *Payment:* {data.get('payment_method', 'Cash on Delivery')}\n"
    wa_text += f"━━━━━━━━━━━━━━━━━━━━\n"
    wa_text += f"*ORDER ITEMS:*\n"

    for idx, item in enumerate(items, 1):
        item_total = float(item.get('price', 0)) * int(item.get('qty', 1))
        wa_text += f"{idx}. {item.get('name')} ({item.get('packaging')}) x {item.get('qty')} = ₹{item_total:,.2f}\n"

    wa_text += f"━━━━━━━━━━━━━━━━━━━━\n"
    wa_text += f"💰 *TOTAL WHOLESALE AMOUNT:* ₹{total_amount:,.2f}\n"
    if data.get('notes'):
        wa_text += f"📝 *Special Note:* {data.get('notes')}\n"
    wa_text += f"━━━━━━━━━━━━━━━━━━━━\n"
    wa_text += f"Placed on Katindhi Valley General Store Web Portal"

    import urllib.parse
    whatsapp_url = f"https://api.whatsapp.com/send?phone={store_owner_phone}&text={urllib.parse.quote(wa_text)}"

    return {
        "order_id": order_id,
        "order_number": order_number,
        "total_amount": total_amount,
        "status": "Pending",
        "created_at": created_at,
        "whatsapp_url": whatsapp_url
    }

def get_orders(status=None, search=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM orders WHERE 1=1"
    params = []

    if status and status.lower() != 'all':
        query += " AND status = ?"
        params.append(status)

    if search:
        query += " AND (order_number LIKE ? OR customer_name LIKE ? OR phone LIKE ? OR shop_name LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term, term])

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    orders = []
    for row in rows:
        try:
            items = json.loads(row["items_json"])
        except Exception:
            items = []
        orders.append({
            "id": row["id"],
            "order_number": row["order_number"],
            "customer_name": row["customer_name"],
            "shop_name": row["shop_name"],
            "phone": row["phone"],
            "address": row["address"],
            "delivery_type": row["delivery_type"],
            "delivery_slot": row["delivery_slot"],
            "payment_method": row["payment_method"],
            "notes": row["notes"],
            "items": items,
            "items_count": len(items),
            "subtotal": row["subtotal"],
            "discount": row["discount"],
            "total_amount": row["total_amount"],
            "status": row["status"],
            "created_at": row["created_at"]
        })
    return orders

def get_order_by_number_or_id(identifier):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE order_number = ? OR id = ? OR phone = ? ORDER BY id DESC LIMIT 1", (identifier, identifier, identifier))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    try:
        items = json.loads(row["items_json"])
    except Exception:
        items = []

    return {
        "id": row["id"],
        "order_number": row["order_number"],
        "customer_name": row["customer_name"],
        "shop_name": row["shop_name"],
        "phone": row["phone"],
        "address": row["address"],
        "delivery_type": row["delivery_type"],
        "delivery_slot": row["delivery_slot"],
        "payment_method": row["payment_method"],
        "notes": row["notes"],
        "items": items,
        "items_count": len(items),
        "subtotal": row["subtotal"],
        "discount": row["discount"],
        "total_amount": row["total_amount"],
        "status": row["status"],
        "created_at": row["created_at"]
    }

def update_order_status(order_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ? OR order_number = ?", (new_status, order_id, order_id))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    return rows_affected > 0

def add_product(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO products (
        name, hindi_name, category, packaging, wholesale_price, retail_mrp,
        moq, unit, stock, image_category, description, is_featured
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("hindi_name", ""),
        data.get("category", "General"),
        data.get("packaging", "Standard Pack"),
        float(data.get("wholesale_price", 0)),
        float(data.get("retail_mrp", 0)),
        int(data.get("moq", 1)),
        data.get("unit", "Pack"),
        int(data.get("stock", 100)),
        data.get("image_category", "grain"),
        data.get("description", ""),
        1 if data.get("is_featured") else 0
    ))
    conn.commit()
    pid = cursor.lastrowid
    conn.close()
    return pid

def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(total_amount), 0) FROM orders")
    total_orders, total_sales = cursor.fetchone()

    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Pending'")
    pending_orders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    conn.close()
    return {
        "total_orders": total_orders,
        "total_sales": round(total_sales, 2),
        "pending_orders": pending_orders,
        "total_products": total_products
    }

if __name__ == "__main__":
    init_db()
