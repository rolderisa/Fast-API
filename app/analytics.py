import pandas as pd
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Dict, Any, List
from . import models
from sqlalchemy import func
from .models import Order, Product,Customer
from sqlalchemy.sql import case
from datetime import date

class FashionStoreAnalytics:
    def __init__(self, db: Session):
        self.db = db
        self.products_df = self._get_products_df()
        self.sales_df = self._get_sales_df()
        self.customers_df = self._get_customers_df()

    def _get_products_df(self) -> pd.DataFrame:
        try:
            products_query = self.db.query(models.Product).all()
            if not products_query:
                return pd.DataFrame(columns=['id', 'name', 'price', 'category_id', 'stock_quantity'])

            return pd.DataFrame([{
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'category_id': product.category_id,
                'stock_quantity': product.stock_quantity
            } for product in products_query])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting products data: {str(e)}")

    def _get_sales_df(self) -> pd.DataFrame:
        try:
            sales_query = self.db.query(models.Order).all()
            if not sales_query:
                return pd.DataFrame(columns=['id', 'product_id', 'customer_id', 'quantity', 'order_date'])

            return pd.DataFrame([{
                'id': order.id,
                'product_id': order.product_id,
                'customer_id': order.customer_id,
                'quantity': order.quantity,
                'order_date': order.order_date
            } for order in sales_query])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting sales data: {str(e)}")

    def _get_customers_df(self) -> pd.DataFrame:
        try:
            customers_query = self.db.query(models.Customer).all()
            if not customers_query:
                return pd.DataFrame(columns=['id', 'name', 'email'])

            return pd.DataFrame([{
                'id': customer.id,
                'name': customer.name,
                'email': customer.email
            } for customer in customers_query])
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting customers data: {str(e)}")

    def get_product_sales_stats(self) -> Dict[str, Any]:
        try:
            if self.sales_df.empty or self.products_df.empty:
                return {'product_sales': {}, 'total_sales': 0}

           
            sales_product_df = pd.merge(self.sales_df, self.products_df, left_on='product_id', right_on='id')
            sales_product_df['total_sales_value'] = sales_product_df['quantity'] * sales_product_df['price']

            
            product_sales_stats = sales_product_df.groupby('name').agg(
                total_sales_value=('total_sales_value', 'sum'),
                quantity_sold=('quantity', 'sum')
            ).reset_index()

            total_sales = product_sales_stats['total_sales_value'].sum()

            return {
                'product_sales': product_sales_stats.to_dict(orient='records'),
                'total_sales': total_sales
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calculating product sales stats: {str(e)}")

    def get_sales_by_category(self) -> Dict[str, Any]:
        try:
            if self.sales_df.empty or self.products_df.empty:
                return {'category_sales': {}, 'total_sales_by_category': {}}

            
            sales_category_df = pd.merge(self.sales_df, self.products_df, left_on='product_id', right_on='id')

            
            category_sales_stats = sales_category_df.groupby('category_id').agg(
                total_sales_value=('quantity', 'sum')
            ).reset_index()

            
            category_sales_stats = category_sales_stats.merge(
                self.db.query(models.Category).all(),
                left_on='category_id',
                right_on='id',
                suffixes=('_category', '_name')
            )

            return {
                'category_sales': category_sales_stats.to_dict(orient='records'),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calculating category sales stats: {str(e)}")

    def get_customer_purchase_analysis(self) -> Dict[str, Any]:
        try:
            if self.sales_df.empty or self.customers_df.empty:
                return {'customer_purchase_analysis': {}}

            
            sales_customer_df = pd.merge(self.sales_df, self.customers_df, left_on='customer_id', right_on='id')

           
            sales_customer_df['total_spent'] = sales_customer_df['quantity'] * sales_customer_df['price']
            customer_analysis = sales_customer_df.groupby('name').agg(
                total_spent=('total_spent', 'sum'),
                total_purchases=('quantity', 'sum')
            ).reset_index()

            return {
                'customer_purchase_analysis': customer_analysis.to_dict(orient='records'),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error analyzing customer purchases: {str(e)}")

    def get_inventory_status(self) -> Dict[str, Any]:
        try:
            if self.products_df.empty:
                return {'inventory_status': {}}

            
            inventory_status = self.products_df[['name', 'stock_quantity']].sort_values(by='stock_quantity', ascending=False)

            return {'inventory_status': inventory_status.to_dict(orient='records')}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error analyzing inventory status: {str(e)}")
    
    def get_total_sales(self):
        
        total_sales = (
            self.db.query(Order, Product)
            .join(Product, Product.id == Order.product_id)
            .with_entities((Order.quantity * Product.price).label("sales"))
        )

        total = sum(row.sales for row in total_sales)
        return total 





    def get_best_selling_products(self, top_n: int = 5):
        """Fetches the top N best-selling products based on order quantity."""
        best_selling_products = (
            self.db.query(Product.name, func.sum(Order.quantity).label("total_quantity"))
            .join(Order, Order.product_id == Product.id)
            .group_by(Product.id)
            .order_by(func.sum(Order.quantity).desc())
            .limit(top_n)
        )

        products = []
        for product, total_quantity in best_selling_products:
            products.append({
                "product_name": product,
                "total_quantity_sold": total_quantity
            })

        return products
    
    def get_sales_by_product(self):
        """Returns the total sales by each product."""
        sales_by_product = (
            self.db.query(Product.name, (Order.quantity * Product.price).label("total_sales"))
            .join(Order, Order.product_id == Product.id)
            .group_by(Product.id)
        )
        return sales_by_product

    def get_product_sales_distribution(self):
        """Calculates the sales distribution across all products."""
        distribution = (
            self.db.query(Product.name, (Order.quantity * Product.price).label("total_sales"))
            .join(Order, Order.product_id == Product.id)
            .group_by(Product.id)
        )
        sales_distribution = []
        for product, total_sales in distribution:
            sales_distribution.append({
                "product_name": product,
                "total_sales": total_sales
            })
        return sales_distribution



    def get_customer_demographics(self):
        """Fetches the customer demographics, such as the total number of customers and their gender or location."""
        demographics = (
            self.db.query(
                func.count(Customer.id).label("total_customers"),
                func.sum(case((Customer.gender == "Male", 1), else_=0)).label("male_count"),
                func.sum(case((Customer.gender == "Female", 1), else_=0)).label("female_count"),
                func.avg(
                    func.strftime('%Y', 'now') - func.strftime('%Y', Customer.birthdate)
                ).label("average_age"),
            )
            .first()
        )

        if demographics:
            return {
                "total_customers": demographics.total_customers,
                "male_count": demographics.male_count,
                "female_count": demographics.female_count,
                "average_age": demographics.average_age,
            }
        return {"detail": "No customer demographics data available"}

    
     