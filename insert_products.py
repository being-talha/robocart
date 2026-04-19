import sqlite3

conn = sqlite3.connect("shopping_cart.db")
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

products = [
    ("123", "Apple", 100, "apple.jpg", 20),
    ("456", "Milk", 250, "milk.jpg", 15),
    ("789", "Bread", 150, "bread.jpg", 10)
]

cur.executemany("INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?, ?)", products)

conn.commit()
conn.close()

print("Products inserted!")