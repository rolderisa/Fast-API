from sqlalchemy.orm import Session
from . import models, schemas
# In crud.py
from app.models import Product,Customer






def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()


# Products
def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Customer).offset(skip).limit(limit).all()


# def get_products(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(Product).offset(skip).limit(limit).all()

def get_products(db: Session):
    return db.query(models.Product).all() 

def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

# Customers
def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer



# Orders
def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session):
    return db.query(models.Order).all()



def update_product(db, product_id: int, product_data):
    product_dict = product_data.dict(exclude_unset=True)  # Convert to dict, ignoring unset fields
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        return None
    for key, value in product_dict.items():
        setattr(db_product, key, value)  # Update attributes dynamically
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
   
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
        return {"msg": "Product deleted successfully"}
    return {"msg": "Product not found"}

def get_customer(db: Session, customer_id: int):
   
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    return customer


def update_customer(db: Session, customer_id: int, customer_data: dict):
    
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()

    if customer:
       
        for key, value in customer_data.items():
            setattr(customer, key, value)
        db.commit()
        db.refresh(customer)
        return customer
    return None


def get_order(db: Session, order_id: int):
   
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def get_orders_by_customer(db: Session, customer_id: int):
    
    return db.query(models.Order).filter(models.Order.customer_id == customer_id).all()