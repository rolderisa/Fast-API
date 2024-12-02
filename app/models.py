from sqlalchemy import Column, Integer, String, Float, ForeignKey,Date
from sqlalchemy.orm import relationship,declarative_base

from datetime import datetime 

from fastapi import FastAPI
Base = declarative_base()

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Fashion Store API!"}


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)  # Make sure this matches
    stock_quantity = Column(Integer, default=0)
    category = relationship("Category", back_populates="products")
    order = relationship("Order", back_populates="product")

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, index=True)  # Make sure the primary key is category_id
    name = Column(String(100), nullable=False, unique=True)

    products = relationship("Product", back_populates="category")

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    gender = Column(String(100), nullable=True) 
    birthdate = Column(Date)
    order=relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    order_date = Column(String(100), default=datetime.utcnow)

    product = relationship("Product", back_populates="order")
    customer = relationship("Customer", back_populates="order")


    
