import sqlite3
import os

db_path = os.path.abspath("shopping_cart.db")
print("Seeding DB:", db_path)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

products = [
    ("1845", "Apple", 100, "apple.jpg", 20),
    ("456", "Milk", 250, "milk.jpg", 15),
    ("789", "Bread", 150, "bread.jpg", 10)
]

cur.executemany("""
    INSERT INTO products (barcode, name, price, image, stock)
    VALUES (?, ?, ?, ?, ?)
""", products)

conn.commit()

cur.execute("SELECT * FROM products")
print("Products now in DB:", cur.fetchall())

conn.close()
print("Products inserted!")