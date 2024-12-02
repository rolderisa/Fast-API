import mysql.connector
from faker import Faker
from random import randint, choice
import random
from datetime import datetime
from tqdm import tqdm


fake = Faker()


db_config = {
    'host': 'localhost',
    'user': 'root',
    'database': 'stores'
}


def create_tables(cursor):
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE
    )""")

    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        category_id INT NOT NULL,
        stock_quantity INT DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
    )""")

    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        gender VARCHAR(50),
        birthdate DATE
    )""")

    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        customer_id INT NOT NULL,
        quantity INT NOT NULL,
        order_date DATE,
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )""")

def generate_fake_data(batch_size=500000):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        
        create_tables(cursor)
        
       
        categories = ["Clothing", "Accessories", "Bags", "Shoes"]
        category_ids = {}
        
        for category in categories:
            cursor.execute("INSERT IGNORE INTO categories (name) VALUES (%s)", (category,))
            cursor.execute("SELECT category_id FROM categories WHERE name = %s", (category,))
            category_ids[category] = cursor.fetchone()[0]
        
        conn.commit()

        
        print("Generating customers...")
        customer_count = batch_size // 5
        for _ in tqdm(range(customer_count)):
            cursor.execute("""
                INSERT INTO customers (name, email, gender, birthdate)
                VALUES (%s, %s, %s, %s)
            """, (
                fake.name(),
                fake.unique.email(),
                choice(["Male", "Female"]),
                fake.date_of_birth(minimum_age=18, maximum_age=80)
            ))
            if _ % 1000 == 0:
                conn.commit()
        
        conn.commit()

       
        print("Generating products and orders...")
        for i in tqdm(range(batch_size)):
            
            category = random.choice(categories)
            cursor.execute("""
                INSERT INTO products (name, price, category_id, stock_quantity)
                VALUES (%s, %s, %s, %s)
            """, (
                fake.word(),
                round(random.uniform(10, 1000), 2),
                category_ids[category],
                randint(1, 1000)
            ))
            product_id = cursor.lastrowid
            
            # Insert order
            cursor.execute("""
                INSERT INTO orders (product_id, customer_id, quantity, order_date)
                VALUES (%s, %s, %s, %s)
            """, (
                product_id,
                randint(1, customer_count),
                randint(1, 10),
                fake.date_this_decade()
            ))
            
            if i % 1000 == 0:
                conn.commit()
        
        conn.commit()
        print(f"Successfully generated {batch_size} products, {customer_count} customers, and {batch_size} orders")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    generate_fake_data(500000)