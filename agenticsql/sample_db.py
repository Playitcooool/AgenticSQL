"""Example database generator for local testing."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import random
import sqlite3


def create_example_database(db_path: str) -> Path:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            city TEXT,
            country TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0
        )
        """
    )

    cursor.execute(
        """
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
        """
    )

    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
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
            "INSERT INTO customers (name, email, city, country) VALUES (?, ?, ?, ?)", customers
        )

    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
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
            "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)", products
        )

    cursor.execute("SELECT COUNT(*) FROM orders")
    if cursor.fetchone()[0] == 0:
        orders = []
        base_date = datetime.now() - timedelta(days=90)
        for _ in range(120):
            customer_id = random.randint(1, 8)
            product_id = random.randint(1, 10)
            quantity = random.randint(1, 5)
            cursor.execute("SELECT price FROM products WHERE product_id = ?", (product_id,))
            price = cursor.fetchone()[0]
            total_amount = price * quantity
            order_date = base_date + timedelta(days=random.randint(0, 90))
            orders.append((customer_id, product_id, quantity, total_amount, order_date))

        cursor.executemany(
            "INSERT INTO orders (customer_id, product_id, quantity, total_amount, order_date) VALUES (?, ?, ?, ?, ?)",
            orders,
        )

    conn.commit()
    conn.close()
    return path
