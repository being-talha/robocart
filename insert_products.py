import sqlite3

conn = sqlite3.connect("shopping_cart.db")
cur = conn.cursor()

products = [
    ("123", "Apple", 100, "apple.jpg"),
    ("456", "Milk", 250, "milk.jpg"),
    ("789", "Bread", 150, "bread.jpg")
]

cur.executemany("INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)", products)

conn.commit()
conn.close()

print("Products inserted successfully!")