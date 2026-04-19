from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect("shopping_cart.db")


# -----------------------
# INIT DB
# -----------------------
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        barcode TEXT PRIMARY KEY,
        name TEXT,
        price INTEGER,
        image TEXT,
        stock INTEGER DEFAULT 10
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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total INTEGER,
        payment TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        name TEXT,
        price INTEGER,
        qty INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()


# -----------------------
# ROUTES
# -----------------------
@app.route("/")
def home():
    return render_template("welcome.html")

@app.route("/shop")
def shop():
    return render_template("index.html")


# -----------------------
# SEARCH
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
    return jsonify({"status": "not_found"})


# -----------------------
# ADD
# -----------------------
@app.route("/add", methods=["POST"])
def add():
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT qty FROM cart WHERE name=?", (data["name"],))
    item = cur.fetchone()

    if item:
        cur.execute("UPDATE cart SET qty = qty + 1 WHERE name=?", (data["name"],))
    else:
        cur.execute("INSERT INTO cart (name, price, qty) VALUES (?, ?, ?)",
                    (data["name"], data["price"], 1))

    conn.commit()
    return get_cart(conn)


# -----------------------
# REMOVE
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
    return get_cart(conn)


# -----------------------
# GET CART
# -----------------------
def get_cart(conn):
    cur = conn.cursor()
    cur.execute("SELECT name, price, qty FROM cart")
    rows = cur.fetchall()

    items = []
    total = 0

    for r in rows:
        subtotal = r[1] * r[2]
        total += subtotal
        items.append({"name": r[0], "qty": r[2], "subtotal": subtotal})

    return jsonify({"items": items, "total": total})


# -----------------------
# CHECKOUT
# -----------------------
@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.get_json()
    payment = data.get("payment", "cash")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT name, price, qty FROM cart")
    items = cur.fetchall()

    if not items:
        return jsonify({"status": "empty"})

    total = sum(i[1] * i[2] for i in items)

    # create order
    cur.execute("INSERT INTO orders (total, payment) VALUES (?, ?)", (total, payment))
    order_id = cur.lastrowid

    for i in items:
        cur.execute("""
        INSERT INTO order_items (order_id, name, price, qty)
        VALUES (?, ?, ?, ?)
        """, (order_id, i[0], i[1], i[2]))

        # reduce stock
        cur.execute("UPDATE products SET stock = stock - ? WHERE name=?", (i[2], i[0]))

    # clear cart
    cur.execute("DELETE FROM cart")

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "order_id": order_id,
        "items": [{"name": i[0], "price": i[1], "qty": i[2]} for i in items],
        "total": total
    })


if __name__ == "__main__":
    app.run(debug=True)