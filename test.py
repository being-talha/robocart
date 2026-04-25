import sqlite3

conn = sqlite3.connect("shopping_cart.db")
cur = conn.cursor()

cur.execute("UPDATE products SET stock = 200")

conn.commit()
print("Stock updated!")