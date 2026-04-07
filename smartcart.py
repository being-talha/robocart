from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# ----------------------------
# Paths
# ----------------------------
IMAGE_FOLDER = r"C:\Users\Dell\Downloads\robocart\images"
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# ----------------------------
# Database
# ----------------------------
def get_db():
    conn = sqlite3.connect("shopping_cart.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create bills table if not exists
conn = get_db()
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS bills (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    quantity INTEGER,
    price REAL,
    total_amount REAL,
    date_time TEXT
)
""")
conn.commit()
conn.close()

# ----------------------------
# Cart (in-memory)
# ----------------------------
cart = {}

# ----------------------------
# Routes for pages
# ----------------------------
@app.route("/")
def welcome():
    return send_from_directory(".", "welcome.html")

@app.route("/shop")
def shop():
    return send_from_directory(".", "index.html")

@app.route("/images/<filename>")
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

# ----------------------------
# API Routes
# ----------------------------
@app.route("/search", methods=["POST"])
def search_product():
    data = request.json
    barcode = data.get("barcode")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, price, image_path FROM products WHERE barcode=?", (barcode,))
    result = cur.fetchone()
    conn.close()

    if result:
        return jsonify({
            "status": "found",
            "name": result["name"],
            "price": result["price"],
            "image": os.path.basename(result["image_path"])
        })
    else:
        return jsonify({"status": "not_found"})

@app.route("/add", methods=["POST"])
def add_to_cart():
    data = request.json
    name = data["name"]
    price = data["price"]

    if name in cart:
        cart[name]["qty"] += 1
    else:
        cart[name] = {"price": price, "qty": 1}

    return jsonify(cart_summary())

@app.route("/remove", methods=["POST"])
def remove_from_cart():
    data = request.json
    name = data["name"]

    if name in cart:
        cart[name]["qty"] -= 1
        if cart[name]["qty"] == 0:
            del cart[name]

    return jsonify(cart_summary())

def cart_summary():
    total = 0
    items = []
    for item in cart:
        qty = cart[item]["qty"]
        price = cart[item]["price"]
        subtotal = qty * price
        total += subtotal
        items.append({"name": item, "qty": qty, "subtotal": subtotal})
    return {"items": items, "total": total}

# ----------------------------
# Run server
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)