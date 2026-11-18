git init
git add .
git commit -m "Katindhi Valley Store"
git branch -M main#!/usr/bin/env python3
"""
Katindhi Valley General Store - Backend Server
Wholesale Grocery Store Web Application
Owner: Hitesh Gupta (9418301840)
Timings: 8:00 AM to 5:00 PM, Monday to Saturday
"""

import os
import sys
import json -uorigin 
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from datetime import datetime
import mimetypes

# Import database layer
import database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads for concurrency."""
    daemon_threads = True

class StoreRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for modern web interaction
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json_response(self, data, status_code=200):
        response_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def send_html_file(self, filepath, status_code=200):
        if not os.path.exists(filepath):
            self.send_error(404, "File Not Found")
            return
        with open(filepath, 'rb') as f:
            content = f.read()
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def parse_json_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        raw_body = self.rfile.read(content_length).decode('utf-8')
        try:
            return json.loads(raw_body)
        except json.JSONDecodeError:
            return {}

    def get_store_status(self):
        """Calculates store open/closed status based on timings: 8:00 AM - 5:00 PM, Mon-Sat"""
        now = datetime.now()
        weekday = now.weekday() # Monday=0, Saturday=5, Sunday=6
        current_time = now.time()

        start_time = datetime.strptime("08:00", "%H:%M").time()
        end_time = datetime.strptime("17:00", "%H:%M").time()

        is_open_day = (weekday < 6) # Monday to Saturday
        is_open_hour = (start_time <= current_time <= end_time)
        is_open = is_open_day and is_open_hour

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        current_day_name = day_names[weekday]

        if is_open:
            status_text = "🟢 OPEN NOW (8:00 AM - 5:00 PM)"
            notice = "Store is currently open for bulk delivery & pickup dispatch."
        elif not is_open_day:
            status_text = "🟠 CLOSED TODAY (Sunday)"
            notice = "Store is closed on Sunday. You can still place online orders; dispatch starts Monday 8:00 AM."
        elif current_time < start_time:
            status_text = "🟠 CURRENTLY CLOSED"
            notice = f"Store opens today ({current_day_name}) at 8:00 AM. Orders placed now will be packed first."
        else:
            status_text = "🟠 CLOSED FOR TODAY"
            next_day = "Monday" if weekday == 5 else "Tomorrow"
            notice = f"Store closed at 5:00 PM. Opens {next_day} at 8:00 AM. Orders are accepted 24/7."

        return {
            "is_open": is_open,
            "status_text": status_text,
            "notice": notice,
            "current_day": current_day_name,
            "current_time": now.strftime("%I:%M %p"),
            "timings": "8:00 AM - 5:00 PM",
            "operating_days": "Monday to Saturday",
            "owner": "Hitesh Gupta",
            "phone": "9418301840",
            "store_name": "Katindhi Valley General Store",
            "hindi_name": "कटिंढी वैली जनरल स्टोर",
            "whatsapp_number": "919418301840"
        }

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Single string extractor helper
        def q(key, default=None):
            return query_params.get(key, [default])[0]

        # 1. Front-end HTML routes
        if path == "/" or path == "/index.html":
            self.send_html_file(os.path.join(TEMPLATES_DIR, "index.html"))
            return
        elif path == "/admin" or path == "/admin.html":
            self.send_html_file(os.path.join(TEMPLATES_DIR, "admin.html"))
            return

        # 2. REST API routes
        elif path == "/api/store-info":
            settings = database.get_store_settings()
            live_status = self.get_store_status()
            data = {**settings, **live_status}
            self.send_json_response({"success": True, "data": data})
            return

        elif path == "/api/categories":
            categories = database.get_categories()
            self.send_json_response({"success": True, "categories": categories})
            return

        elif path == "/api/products":
            category = q("category")
            search = q("search")
            sort = q("sort")
            featured = q("featured") == "1" or q("featured") == "true"
            products = database.get_products(category=category, search=search, featured=featured, sort=sort)
            self.send_json_response({"success": True, "count": len(products), "products": products})
            return

        elif path.startswith("/api/products/"):
            try:
                prod_id = int(path.split("/api/products/")[1])
                product = database.get_product_by_id(prod_id)
                if product:
                    self.send_json_response({"success": True, "product": product})
                else:
                    self.send_json_response({"success": False, "error": "Product not found"}, 404)
            except ValueError:
                self.send_json_response({"success": False, "error": "Invalid product ID"}, 400)
            return

        elif path == "/api/orders":
            status = q("status")
            search = q("search")
            orders = database.get_orders(status=status, search=search)
            self.send_json_response({"success": True, "count": len(orders), "orders": orders})
            return

        elif path.startswith("/api/orders/"):
            identifier = path.split("/api/orders/")[1]
            order = database.get_order_by_number_or_id(identifier)
            if order:
                self.send_json_response({"success": True, "order": order})
            else:
                self.send_json_response({"success": False, "error": "Order not found"}, 404)
            return

        elif path == "/api/stats":
            stats = database.get_stats()
            self.send_json_response({"success": True, "stats": stats})
            return

        # 3. Static files route (/static/*)
        elif path.startswith("/static/"):
            rel_path = path[len("/static/"):]
            full_path = os.path.join(STATIC_DIR, rel_path)
            # Security check against path traversal
            if os.path.commonpath([STATIC_DIR, os.path.abspath(full_path)]) != STATIC_DIR:
                self.send_error(403, "Forbidden")
                return

            if os.path.exists(full_path) and os.path.isfile(full_path):
                mime_type, _ = mimetypes.guess_type(full_path)
                mime_type = mime_type or 'application/octet-stream'
                try:
                    with open(full_path, 'rb') as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', mime_type)
                    self.send_header('Content-Length', str(len(content)))
                    self.send_header('Cache-Control', 'public, max-age=3600')
                    self.end_headers()
                    self.wfile.write(content)
                    return
                except Exception as e:
                    self.send_error(500, f"Error reading static file: {str(e)}")
                    return
            else:
                self.send_error(404, "Static File Not Found")
                return

        # Fallback 404
        self.send_error(404, "Page Not Found")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        body = self.parse_json_body()

        if path == "/api/orders":
            # Validate required fields
            if not body.get("customer_name") or not body.get("phone"):
                self.send_json_response({"success": False, "error": "Customer name and phone number are required"}, 400)
                return
            if not body.get("items") or len(body.get("items")) == 0:
                self.send_json_response({"success": False, "error": "Cart is empty"}, 400)
                return

            try:
                order_result = database.create_order(body)
                self.send_json_response({
                    "success": True,
                    "message": "Wholesale order placed successfully!",
                    "data": order_result
                }, 201)
            except Exception as e:
                self.send_json_response({"success": False, "error": f"Failed to save order: {str(e)}"}, 500)
            return

        elif path == "/api/orders/update-status":
            order_id = body.get("order_id")
            new_status = body.get("status")
            if not order_id or not new_status:
                self.send_json_response({"success": False, "error": "order_id and status are required"}, 400)
                return

            updated = database.update_order_status(order_id, new_status)
            if updated:
                self.send_json_response({"success": True, "message": f"Order status updated to {new_status}"})
            else:
                self.send_json_response({"success": False, "error": "Order not found or update failed"}, 404)
            return

        elif path == "/api/products":
            if not body.get("name") or not body.get("wholesale_price"):
                self.send_json_response({"success": False, "error": "Product name and wholesale price are required"}, 400)
                return

            pid = database.add_product(body)
            self.send_json_response({"success": True, "message": "Product added successfully", "product_id": pid}, 201)
            return

        self.send_error(404, "API Endpoint Not Found")

def run(port=8080):
    database.init_db()
    server_address = ('', port)
    httpd = ThreadedHTTPServer(server_address, StoreRequestHandler)
    print("=" * 60)
    print(f" Katindhi Valley General Store - Wholesale Web Server")
    print(f" Owner: Hitesh Gupta | Phone: 9418301840")
    print(f" Timings: 8:00 AM to 5:00 PM (Mon - Sat)")
    print(f" Store URL:        http://localhost:{port}/")
    print(f" Owner Dashboard:  http://localhost:{port}/admin")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down gracefully.")
        httpd.server_close()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run(port)
