from flask import Flask, render_template, request, jsonify, send_from_directory
import sqlite3

app = Flask(__name__)

# -----------------------
# Database connection
# -----------------------
def get_db():
    return sqlite3.connect("shopping_cart.db")


# -----------------------
# Create tables (run once)
# -----------------------
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        barcode TEXT PRIMARY KEY,
        name TEXT,
        price INTEGER,
        image TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        qty INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()


# -----------------------
# Routes (Frontend Pages)
# -----------------------
@app.route("/")
def home():
    return render_template("welcome.html")

@app.route("/shop")
def shop():
    return render_template("index.html")


# -----------------------
# Search Product
# -----------------------
@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    barcode = data["barcode"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM products WHERE barcode=?", (barcode,))
    product = cur.fetchone()

    conn.close()

    if product:
        return jsonify({
            "status": "found",
            "barcode": product[0],
            "name": product[1],
            "price": product[2],
            "image": product[3]
        })
    else:
        return jsonify({"status": "not_found"})


# -----------------------
# Add to Cart
# -----------------------
@app.route("/add", methods=["POST"])
def add():
    data = request.get_json()

    conn = get_db()
    cur = conn.cursor()

    # check if already in cart
    cur.execute("SELECT qty FROM cart WHERE name=?", (data["name"],))
    item = cur.fetchone()

    if item:
        cur.execute("UPDATE cart SET qty = qty + 1 WHERE name=?", (data["name"],))
    else:
        cur.execute("INSERT INTO cart (name, price, qty) VALUES (?, ?, ?)",
                    (data["name"], data["price"], 1))

    conn.commit()

    return get_cart_response(conn)


# -----------------------
# Remove from Cart
# -----------------------
@app.route("/remove", methods=["POST"])
def remove():
    data = request.get_json()

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT qty FROM cart WHERE name=?", (data["name"],))
    item = cur.fetchone()

    if item:
        if item[0] > 1:
            cur.execute("UPDATE cart SET qty = qty - 1 WHERE name=?", (data["name"],))
        else:
            cur.execute("DELETE FROM cart WHERE name=?", (data["name"],))

    conn.commit()

    return get_cart_response(conn)


# -----------------------
# Cart Response Helper
# -----------------------
def get_cart_response(conn):
    cur = conn.cursor()
    cur.execute("SELECT name, price, qty FROM cart")
    rows = cur.fetchall()

    items = []
    total = 0

    for row in rows:
        subtotal = row[1] * row[2]
        total += subtotal

        items.append({
            "name": row[0],
            "qty": row[2],
            "subtotal": subtotal
        })

    return jsonify({
        "items": items,
        "total": total
    })


# -----------------------
# Serve Images
# -----------------------
@app.route("/images/<filename>")
def images(filename):
    return send_from_directory("static/images", filename)


# -----------------------
# Run App
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)