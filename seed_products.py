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
    ("999", "Eggs", 300, "eggs.jpg", 30),
    ("8991111101316", "Johnson's Baby Oil", 450, "johnson-baby-oil.png", 50),
    ("8964000061534", "Young's Chicken Spread",310, "chicken-spread.png", 20),
    ("6920247173227", "Rhode Lip tint",500, "rhode-lip-tint.png", 20),
    ("8964003594084", "Peek Frean's Cake Up", 40, "cupcake.png", 30),  
    ("8961003652318", "Oreo Chocolate", 30, "oreo.png", 30),
    
      
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

