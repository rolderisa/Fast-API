from app.database import SessionLocal
from app.models import Customer, Product, Order, Category
from datetime import datetime, timedelta
import random

def create_test_data():
    db = SessionLocal()
    try:
        # Deleting any existing data
        db.query(Customer).delete()
        db.query(Product).delete()
        db.query(Order).delete()
        db.query(Category).delete()
        db.commit()

        # Creating Categories
        categories = [
            Category(name="Clothing"),
            Category(name="Accessories"),
            Category(name="Footwear"),
            Category(name="Jewelry")
        ]
        db.add_all(categories)
        db.commit()

        # Creating Customers
        customers = [
            Customer(
                name=f"Customer {i}",
                email=f"customer{i}@example.com",
                # phone=f"+1234567890{i}",
                # address=f"Address {i}",
                # registered_on=datetime.now() - timedelta(days=random.randint(0, 365))
            ) for i in range(1, 11)
        ]
        db.add_all(customers)
        db.commit()

        # Creating Products
        products = [
            Product(
                name=f"Product {i}",
                # description=f"Description of Product {i}",
                price=random.uniform(10, 500),
                # stock=random.randint(1, 100),
                category_id=random.choice([cat.id for cat in categories])
            ) for i in range(1, 21)
        ]
        db.add_all(products)
        db.commit()

        # Creating Orders
        orders = [
            Order(
                customer_id=random.choice([cust.id for cust in customers]),
                product_id=random.choice([prod.id for prod in products]),
                # order_date=datetime.now() - timedelta(days=random.randint(0, 30)),
                quantity=random.randint(1, 5),
                # total_price=random.uniform(10, 500)
            ) for _ in range(1, 11)
        ]
        db.add_all(orders)
        db.commit()

        print("Test data created successfully!")

    except Exception as e:
        print(f"Error creating test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
