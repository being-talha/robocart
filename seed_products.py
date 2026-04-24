import sqlite3
import os

db_path = os.path.abspath("shopping_cart.db")
print("Seeding/Updating DB:", db_path)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

products = [
    ("1845", "Apple", 199, "apple.png", 20),   # E.g., changed price to 110
    ("456", "Milk", 250, "milk.jpg", 15),
    ("789", "Bread", 150, "bread.jpg", 10),
    ("999", "Eggs", 300, "eggs.jpg", 30)       # Added a new item
]

# The Upsert Query
cur.executemany("""
    INSERT INTO products (barcode, name, price, image, stock)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(barcode) DO UPDATE SET
        name = excluded.name,
        price = excluded.price,
        image = excluded.image,
        stock = excluded.stock
""", products)

conn.commit()

cur.execute("SELECT * FROM products")
print("Products now in DB:")
for row in cur.fetchall():
    print(row)

conn.close()
print("Database updated successfully!")