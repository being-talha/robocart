import sqlite3

conn = sqlite3.connect("shopping_cart.db")
cur = conn.cursor()

# List all tables in the database
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()

print("Tables in database:")
for t in tables:
    print("-", t[0])

conn.close()