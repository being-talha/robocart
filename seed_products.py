import sqlite3
import os

db_path = os.path.abspath("shopping_cart.db")
print("Seeding/Updating DB:", db_path)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

products = [
    ("1845", "Apple", 199, 100, "apple.png", 20),   # E.g., changed price to 110
    ("456", "Milk", 250, 200, "milk.png", 15),
    ("789", "Bread", 150, 150, "bread.jpg", 10),
    ("999", "Eggs", 300, 300, "eggs.jpg", 30),
    ("8991111101316", "Johnson's Baby Oil", 450, 400, "johnson-baby-oil.png", 50),
    ("8964000061534", "Young's Chicken Spread",310, 350, "chicken-spread.png", 20),
    ("6920247173227", "Rhode Lip tint",500, 500, "rhode-lip-tint.png", 20),
    ("8964003594084", "Peek Frean's Cake Up", 40, 40, "cupcake.png", 30),  
    ("8961003652318", "Oreo Chocolate Biscuit", 30, 30, "oreo.png", 30),
    ("8961003679759", "LU Candi Biscuit", 40, 25, "candi.png", 30),
    ("PL159865-200-999-L", "J. Starry Midnight Body Spray", 650, 250, "jdot.png", 10),
    ("8964002346899", "LAYS FRENCH CHEESE", 70, 30, "lays.png", 20),
    ("1234567890128", "ACNE CONTROL FACE WASH", 150, 140, "acne.png", 20),
    ("8964004770616", "PEANUT PIK Biscuit", 70, 30, "peanut_biscuits.png", 20),
    ("8964000346549", "OLPERS Milk 250ml", 90, 260, "olpers.png", 20),
    ("8961003629198", "LU Tuc Biscuit", 50, 70, "lu.png", 40),
]

# The Upsert Query
cur.executemany("""
    INSERT INTO products (barcode, name, price, expected_weight, image, stock)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(barcode) DO UPDATE SET
        name = excluded.name,
        price = excluded.price,
        expected_weight = excluded.expected_weight,
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

