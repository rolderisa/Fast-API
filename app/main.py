from fastapi import FastAPI, Depends, HTTPException,status
from sqlalchemy.orm import Session,sessionmaker
from typing import List
from . import analytics, crud, schemas, models
from .database import engine, get_db,SQLALCHEMY_DATABASE_URL
from sqlalchemy import create_engine,Table, Column, Integer, String, MetaData,func,Float,ForeignKey,Date
import pandas as pd
from .analytics import FashionStoreAnalytics
import requests
from faker import Faker
from pydantic import BaseModel
from .models import Product,Category,Order,Customer
from typing import List, Optional
from datetime import datetime
from sklearn.preprocessing import LabelEncoder

models.Base.metadata.create_all(bind=engine)

class DatasetInfo(BaseModel):
    table_name: str
    row_count: int

class DatasetDescription(BaseModel):
    table_name: str
    description: dict

class NullValueInfo(BaseModel):
    table_name: str
    null_counts: dict

class FeatureInfo(BaseModel):
    feature_name: str
    description: str

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Welcome to the Fashion Store API"}


@app.post("/categories/", response_model=schemas.CategoryCreate)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = crud.create_category(db=db, category=category)
    return db_category

@app.get("/categories/", response_model=List[schemas.Category])  # List of Category schema
def list_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    categories = crud.get_categories(db=db, skip=skip, limit=limit)  # Fetch categories from CRUD
    return categories

@app.post("/products/", response_model=schemas.Product)
def create_product(data: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=data)

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return crud.get_products(db)  



@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product_view(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/products/{product_id}")
def update_product_view(product_id: int, data: schemas.ProductUpdate, db: Session = Depends(get_db)):
    updated_product = crud.update_product(db=db, product_id=product_id, product_data=data)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"msg": "Product updated successfully", "product": updated_product}


@app.delete("/products/{product_id}")
def delete_product_view(product_id: int, db: Session = Depends(get_db)):
    success = crud.delete_product(db=db, product_id=product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"msg": "Product deleted successfully"}


@app.get("/customers/")
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_customers(db=db, skip=skip, limit=limit)


@app.post("/customers/", response_model=schemas.Customer)
def create_customer_view(data: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db=db, customer=data)


@app.get("/customers/{customer_id}")
def read_customer_view(customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db=db, customer_id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.put("/customers/{customer_id}")
def update_customer_view(customer_id: int, data: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    updated_customer = crud.update_customer(db=db, customer_id=customer_id, customer_data=data.dict())
    if not updated_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated_customer


@app.post("/orders/", response_model=schemas.Order)
def create_order_view(data: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db=db, order=data)


@app.get("/orders/{order_id}")
def read_order_view(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order(db=db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.get("/orders/customer/{customer_id}")
def list_orders_by_customer(customer_id: int, db: Session = Depends(get_db)):
    orders = crud.get_orders_by_customer(db=db, customer_id=customer_id)
    if not orders:
        raise HTTPException(status_code=404, detail="Orders not found")
    return orders



@app.get("/analytics/total_sales")
def get_total_sales(db: Session = Depends(get_db)):
    try:
        analytics_instance = FashionStoreAnalytics(db)
        total_sales = analytics_instance.get_total_sales()
        return {"total_sales": total_sales}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting total sales: {e}")


@app.get("/analytics/product-sales-distribution")
def get_product_sales_distribution(db: Session = Depends(get_db)):
    try:
        analytics_instance = FashionStoreAnalytics(db)
        product_sales_distribution = analytics_instance.get_product_sales_distribution()
        return {"product_sales_distribution": product_sales_distribution}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting product sales distribution: {e}")
    
@app.get("/analytics/customer-demographics")
def get_customer_demographics(db: Session = Depends(get_db)):
    try:
        analytics_instance = FashionStoreAnalytics(db)
        demographics = analytics_instance.get_customer_demographics()
        return {"customer_demographics": demographics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting customer demographics: {e}")


@app.get("/analytics/{analysis_type}")
def get_specific_analytics(analysis_type: str, db: Session = Depends(get_db)):
    try:
        analytics_instance = FashionStoreAnalytics(db)
        analysis_map = {
            "total_sales": analytics_instance.get_total_sales,
            "product_sales_distribution": analytics_instance.get_product_sales_distribution,
            "customer_demographics": analytics_instance.get_customer_demographics,
        }
        if analysis_type not in analysis_map:
            raise HTTPException(status_code=404, detail=f"Invalid analysis type: {analysis_type}")
        return analysis_map[analysis_type]()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/fetch-data")
def fetch_data():
    try:
        
        product_api = requests.get('http://127.0.0.1:8000/products')
        product_api.raise_for_status()  
        product_api_data = product_api.json()  

   
        customer_api = requests.get('http://127.0.0.1:8000/customers')
        customer_api.raise_for_status()  
        customer_api_data = customer_api.json()  

      
        customer_id = 1  
        orders_api = requests.get(f'http://127.0.0.1:8000/orders/customer/{customer_id}')  
        orders_api.raise_for_status()  
        orders_api_data = orders_api.json() 
        customer_df = pd.DataFrame(customer_api_data if isinstance(customer_api_data, list) else customer_api_data.get('customers', []))
        print("The customer data frame is:\n{}".format(customer_df))
        product_df = pd.DataFrame(product_api_data if isinstance(product_api_data, list) else product_api_data.get('users', []))
        print("The product data frame is:\n{}".format(product_df))
        merged_df = pd.merge(customer_df, product_df, on='id', how='inner')
        print(merged_df.head())
        print("the null points are: {}".format(merged_df.isnull()))
        print("the sum of null points is: {}".format(merged_df.isnull().sum()))
        
        
        print("Product API Response:", product_api_data)
        print("Customer API Response:", customer_api_data)
        print("Orders API Response:", orders_api_data)

     
        if 'data' in product_api_data and 'columns' in product_api_data:
            pdf = pd.DataFrame(product_api_data['data'], columns=product_api_data['columns'])
            print("Products DataFrame:")
            print(pdf.head()) 
        else:
            print("Product API response does not contain 'data' or 'columns'.")

       
        if 'data' in customer_api_data and 'columns' in customer_api_data:
            cdf = pd.DataFrame(customer_api_data['data'], columns=customer_api_data['columns'])
            print("Customers DataFrame:")
            print(cdf.head()) 
        else:
            print("Customer API response does not contain 'data' or 'columns'.")

        
        if 'data' in orders_api_data and 'columns' in orders_api_data:
            odf = pd.DataFrame(orders_api_data['data'], columns=orders_api_data['columns'])
            print("Orders DataFrame:")
            print(odf.head())  
        else:
            print("Orders API response does not contain 'data' or 'columns'.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")


@app.get("/quiz/question1", response_model=List[DatasetInfo])
def get_dataset_info(db: Session = Depends(get_db)):
    tables = [models.Product, models.Category, models.Customer, models.Order]
    result = []
    for table in tables:
        if table == models.Category:
            row_count = db.query(func.count(table.category_id)).scalar()
        else:
            row_count = db.query(func.count(table.id)).scalar()
        result.append(DatasetInfo(table_name=table.__tablename__, row_count=row_count))
    return result

@app.get("/quiz/question2", response_model=List[DatasetDescription])
def describe_dataset(db: Session = Depends(get_db)):
    tables = [models.Product, models.Category, models.Customer, models.Order]
    result = []
    for table in tables:
        df = pd.read_sql(db.query(table).statement, db.bind)
        description = df.describe().to_dict()
        result.append(DatasetDescription(table_name=table.__tablename__, description=description))
    return result


@app.get("/quiz/question3", response_model=List[NullValueInfo])
def find_null_values(db: Session = Depends(get_db)):
    tables = [models.Product, models.Category, models.Customer, models.Order]
    result = []
    for table in tables:
        df = pd.read_sql(db.query(table).statement, db.bind)
        null_counts = df.isnull().sum().to_dict()
        result.append(NullValueInfo(table_name=table.__tablename__, null_counts=null_counts))
    return result

@app.post("/quiz/question3/replace_nulls")
def replace_null_values(db: Session = Depends(get_db)):
    db.query(models.Product).filter(models.Product.stock_quantity.is_(None)).update({"stock_quantity": 0})
    db.query(models.Customer).filter(models.Customer.gender.is_(None)).update({"gender": "Unknown"})
    db.commit()
    return {"message": "Null values replaced successfully"}



@app.get("/quiz/question4")
def basic_preprocessing(db: Session = Depends(get_db)):
 
    try:
   
        products_df = pd.read_sql(db.query(models.Product).statement, db.bind)
        customers_df = pd.read_sql(db.query(models.Customer).statement, db.bind)
        orders_df = pd.read_sql(db.query(models.Order).statement, db.bind)

       
        print("\n=== NORMALIZING PRODUCT PRICES ===")
        products_df['normalized_price'] = (
            (products_df['price'] - products_df['price'].mean()) / products_df['price'].std()
        )

        print("\n=== CONVERTING ORDER DATES TO DATETIME ===")
        orders_df['order_date'] = pd.to_datetime(
            orders_df['order_date'], format='mixed', errors='coerce'
        )

      
        print("\n=== PROCESSING CUSTOMER DATA ===")
        customers_df['birthdate'] = pd.to_datetime(
            customers_df['birthdate'], format='mixed', errors='coerce'
        )
        current_date = pd.Timestamp.now()

      
        customers_df['age'] = (current_date - customers_df['birthdate']).dt.days / 365.25
        customers_df['age'] = customers_df['age'].fillna(0)  
        customers_df['age'] = customers_df['age'].astype(int)

        return {
            "products_sample": products_df.head().to_dict(orient='records'),
            "customers_sample": customers_df.head().to_dict(orient='records'),
            "orders_sample": orders_df.head().to_dict(orient='records'),
        }

    except Exception as e:
        print("\n=== AN ERROR OCCURRED ===")
        print(f"Error: {e}")
        return {"error": str(e)}

@app.get("/quiz/question5", response_model=List[FeatureInfo])
def create_features(db: Session = Depends(get_db)):
    products_df = pd.read_sql(db.query(models.Product).statement, db.bind)
    customers_df = pd.read_sql(db.query(models.Customer).statement, db.bind)
    orders_df = pd.read_sql(db.query(models.Order).statement, db.bind)

    product_sales = orders_df.groupby('product_id')['quantity'].sum().reset_index()
    products_df = products_df.merge(product_sales, left_on='id', right_on='product_id', how='left')
    products_df['total_sales'] = products_df['quantity'].fillna(0)

    orders_df['total_value'] = orders_df['quantity'] * orders_df.merge(products_df[['id', 'price']], left_on='product_id', right_on='id')['price']
    customer_avg_order = orders_df.groupby('customer_id')['total_value'].mean().reset_index()
    customers_df = customers_df.merge(customer_avg_order, left_on='id', right_on='customer_id', how='left')
    customers_df['avg_order_value'] = customers_df['total_value'].fillna(0)

    new_features = [
        FeatureInfo(feature_name="total_sales", description="Total sales quantity for each product"),
        FeatureInfo(feature_name="avg_order_value", description="Average order value for each customer")
    ]

    return new_features