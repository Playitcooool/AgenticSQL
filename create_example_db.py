"""
Create example database for testing AgenticSQL
"""
import sqlite3
from datetime import datetime, timedelta
import random


def create_example_database(db_path: str = "example.db"):
    """Create an example database with sample data."""

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create customers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        city TEXT,
        country TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        price REAL NOT NULL,
        stock INTEGER DEFAULT 0
    )
    """)

    # Create orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        product_id INTEGER,
        quantity INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    """)

    # Insert sample customers
    customers = [
        ("Alice Johnson", "alice@example.com", "New York", "USA"),
        ("Bob Smith", "bob@example.com", "London", "UK"),
        ("Charlie Brown", "charlie@example.com", "Toronto", "Canada"),
        ("Diana Prince", "diana@example.com", "Paris", "France"),
        ("Eve Wilson", "eve@example.com", "Sydney", "Australia"),
        ("Frank Miller", "frank@example.com", "Berlin", "Germany"),
        ("Grace Lee", "grace@example.com", "Tokyo", "Japan"),
        ("Henry Davis", "henry@example.com", "Mumbai", "India"),
    ]

    cursor.executemany(
        "INSERT INTO customers (name, email, city, country) VALUES (?, ?, ?, ?)",
        customers
    )

    # Insert sample products
    products = [
        ("Laptop", "Electronics", 999.99, 50),
        ("Smartphone", "Electronics", 699.99, 100),
        ("Headphones", "Electronics", 149.99, 200),
        ("Desk Chair", "Furniture", 299.99, 30),
        ("Standing Desk", "Furniture", 599.99, 20),
        ("Coffee Maker", "Appliances", 89.99, 75),
        ("Blender", "Appliances", 59.99, 60),
        ("Book - Python Programming", "Books", 39.99, 150),
        ("Book - Data Science", "Books", 44.99, 120),
        ("Wireless Mouse", "Electronics", 29.99, 300),
    ]

    cursor.executemany(
        "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
        products
    )

    # Insert sample orders
    orders = []
    base_date = datetime.now() - timedelta(days=90)

    for i in range(50):
        customer_id = random.randint(1, 8)
        product_id = random.randint(1, 10)
        quantity = random.randint(1, 5)

        # Get product price
        cursor.execute("SELECT price FROM products WHERE product_id = ?", (product_id,))
        price = cursor.fetchone()[0]
        total_amount = price * quantity

        # Random date within last 90 days
        order_date = base_date + timedelta(days=random.randint(0, 90))

        orders.append((customer_id, product_id, quantity, total_amount, order_date))

    cursor.executemany(
        "INSERT INTO orders (customer_id, product_id, quantity, total_amount, order_date) VALUES (?, ?, ?, ?, ?)",
        orders
    )

    # Commit and close
    conn.commit()
    conn.close()

    print(f"✅ Database created successfully with:")
    print(f"   - {len(customers)} customers")
    print(f"   - {len(products)} products")
    print(f"   - {len(orders)} orders")


if __name__ == "__main__":
    create_example_database()
