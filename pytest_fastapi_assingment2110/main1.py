# from fastapi import FastAPI
# from pydantic import BaseModel
#
# app = FastAPI()
#
# class Product(BaseModel):
#     id: int
#     name: str
#     price: float
#
# products = []
#
# @app.get("/products")
# def get_products():
#     return products
#
# @app.post("/products")
# def add_product(product: Product):
#     products.append(product)
#     return product