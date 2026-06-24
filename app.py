from flask import Flask, render_template, request, jsonify, session, redirect
from db import get_db, close_db, init_db
import os
import json
import uuid
from datetime import datetime

print("Using DB:", os.path.abspath("shopping_cart.db"))

app = Flask(__name__)
app.secret_key = "your-secret-key"


@app.teardown_appcontext
def teardown_db(exception):
    close_db(exception)


def setup():
    init_db()


setup()


@app.route("/")
def home():
    return render_template("welcome.html")


@app.route("/shop")
def shop():
    return render_template("index.html")


PAYMENTS_FILE = "payments.json"


def load_payments():
    if not os.path.exists(PAYMENTS_FILE):
        return []

    with open(PAYMENTS_FILE, "r") as file:
        return json.load(file)


def save_payments(payments):
    with open(PAYMENTS_FILE, "w") as file:
        json.dump(payments, file, indent=4)


def find_payment(order_ref):
    payments = load_payments()

    for payment in payments:
        if payment["order_ref"] == order_ref:
            return payment

    return None


@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    barcode = str(data.get("barcode", "")).strip()

    if not barcode:
        return jsonify({"status": "error", "message": "Barcode is required"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE barcode = ?", (barcode,))
    product = cur.fetchone()

    if product:
        return jsonify({
            "status": "found",
            "id": product["id"],
            "barcode": product["barcode"],
            "name": product["name"],
            "price": product["price"],
            "image": product["image"],
            "stock": product["stock"]
        })

    return jsonify({"status": "not_found"})


def get_session_cart():
    if "cart" not in session:
        session["cart"] = {}
    return session["cart"]


@app.route("/clear-cart", methods=["POST"])
def clear_cart():
    session["cart"] = {}
    session.modified = True
    return jsonify(build_cart_response())


@app.route("/add", methods=["POST"])
def add():
    data = request.get_json()
    barcode = data.get("barcode", "").strip()

    if not barcode:
        return jsonify({"status": "error", "message": "Barcode is required"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE barcode = ?", (barcode,))
    product = cur.fetchone()

    if not product:
        return jsonify({"status": "error", "message": "Product not found"}), 404

    cart = get_session_cart()
    current_qty = cart.get(barcode, {}).get("qty", 0)

    if current_qty >= product["stock"]:
        return jsonify({"status": "error", "message": "Not enough stock"})

    cart[barcode] = {
        "barcode": product["barcode"],
        "name": product["name"],
        "price": product["price"],
        "image": product["image"],
        "qty": current_qty + 1
    }

    session["cart"] = cart
    session.modified = True

    return jsonify(build_cart_response())


@app.route("/remove", methods=["POST"])
def remove():
    data = request.get_json()
    barcode = str(data.get("barcode", "")).strip()

    if not barcode:
        return jsonify({"status": "error", "message": "Barcode is required"}), 400

    cart = get_session_cart()

    if barcode in cart:
        if cart[barcode]["qty"] > 1:
            cart[barcode]["qty"] -= 1
        else:
            del cart[barcode]

    session["cart"] = cart
    session.modified = True

    return jsonify(build_cart_response())


@app.route("/cart", methods=["GET"])
def cart():
    return jsonify(build_cart_response())


def build_cart_response():
    cart = get_session_cart()
    items = []
    total = 0

    for item in cart.values():
        subtotal = item["price"] * item["qty"]
        total += subtotal
        items.append({
            "barcode": item["barcode"],
            "name": item["name"],
            "price": item["price"],
            "image": item["image"],
            "qty": item["qty"],
            "subtotal": subtotal
        })

    return {"items": items, "total": total}


@app.route("/checkout")
def checkout_page():
    cart_data = build_cart_response()

    if not cart_data["items"]:
        return render_template("index.html", message="Cart is empty")

    tax_rate = 0.05
    subtotal = cart_data["total"]
    tax = round(subtotal * tax_rate, 2)
    grand_total = round(subtotal + tax, 2)

    now = datetime.now()
    order_ref = f"ORD-{uuid.uuid4().hex[:10].upper()}"

    return render_template(
        "checkout.html",
        items=cart_data["items"],
        subtotal=subtotal,
        tax=tax,
        grand_total=grand_total,
        current_date=now.strftime("%d %b %Y"),
        current_time=now.strftime("%I:%M %p"),
        order_ref=order_ref
    )


@app.post("/payment/submit-info")
def submit_payment_info():
    data = request.get_json() or {}

    order_ref = data.get("orderRef")
    payment_method = data.get("paymentMethod")
    sender_number = data.get("senderNumber")
    amount = data.get("amount")

    if not order_ref or not payment_method or not sender_number:
        return jsonify({
            "success": False,
            "message": "Missing payment information."
        }), 400

    payments = load_payments()

    existing = find_payment(order_ref)
    if existing:
        return jsonify({
            "success": False,
            "message": "Payment information already submitted for this order."
        }), 400

    payments.append({
        "order_ref": order_ref,
        "payment_method": payment_method,
        "sender_number": sender_number,
        "amount": amount,
        "status": "PENDING_VERIFICATION",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    save_payments(payments)

    return jsonify({
        "success": True,
        "message": "Payment submitted. Waiting for admin verification.",
        "status": "PENDING_VERIFICATION"
    })


@app.route("/complete-checkout", methods=["POST"])
def complete_checkout():
    data = request.get_json()
    payment = data.get("payment", "cash")

    cart = get_session_cart()
    if not cart:
        return jsonify({"status": "empty"})

    conn = get_db()
    cur = conn.cursor()

    validated_items = []
    total = 0

    for barcode, item in cart.items():
        barcode = str(barcode).strip()
        cur.execute("SELECT * FROM products WHERE barcode = ?", (barcode,))
        product = cur.fetchone()

        if not product:
            return jsonify({"status": "error", "message": f"Product missing: {barcode}"})

        if product["stock"] < item["qty"]:
            return jsonify({
                "status": "error",
                "message": f"Insufficient stock for {product['name']}"
            })

        subtotal = product["price"] * item["qty"]
        total += subtotal

        validated_items.append({
            "product_id": product["id"],
            "barcode": product["barcode"],
            "name": product["name"],
            "price": product["price"],
            "qty": item["qty"],
            "subtotal": subtotal
        })

    cur.execute(
        "INSERT INTO orders (total, payment) VALUES (?, ?)",
        (total, payment)
    )
    order_id = cur.lastrowid

    for item in validated_items:
        cur.execute("""
            INSERT INTO order_items (order_id, product_id, price_at_time, qty, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, (order_id, item["product_id"], item["price"], item["qty"], item["subtotal"]))

        cur.execute("""
            UPDATE products
            SET stock = stock - ?
            WHERE id = ?
        """, (item["qty"], item["product_id"]))

    conn.commit()

    session["cart"] = {}
    session.modified = True

    return jsonify({
        "status": "success",
        "order_id": order_id,
        "items": validated_items,
        "total": total
    })


@app.get("/payment/status/<order_ref>")
def payment_status(order_ref):
    payment = find_payment(order_ref)

    if not payment:
        return jsonify({
            "status": "PENDING_PAYMENT"
        })

    return jsonify({
        "status": payment["status"]
    })


@app.route("/admin/payments")
def admin_payments():
    admin_key = request.args.get("key")

    if admin_key != "12345":
        return "Unauthorized", 403

    payments = load_payments()

    return render_template(
        "admin_payments.html",
        payments=payments
    )


@app.post("/admin/payment/approve/<order_ref>")
def approve_payment(order_ref):
    payments = load_payments()

    for payment in payments:
        if payment["order_ref"] == order_ref:
            payment["status"] = "PAID"
            payment["verified_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_payments(payments)
            break

    session["cart"] = {}
    session.modified = True

    return redirect("/admin/payments?key=12345")


@app.post("/admin/payment/reject/<order_ref>")
def reject_payment(order_ref):
    payments = load_payments()

    for payment in payments:
        if payment["order_ref"] == order_ref:
            payment["status"] = "REJECTED"
            payment["verified_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_payments(payments)
            break

    return redirect("/admin/payments?key=12345")


@app.route("/thankyou")
def thankyou():
    order_ref = request.args.get("orderRef", "N/A")
    return render_template("thankyou.html", order_ref=order_ref)


 # app.run(host="0.0.0.0", port=5000, debug=True)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)