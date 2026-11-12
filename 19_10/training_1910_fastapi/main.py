from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Product(BaseModel):
    id: int
    name: str
    price: float

products = []

@app.get("/products")
def get_products():
    return products

@app.post("/products")
def add_product(product: Product):
    products.append(product)
    return {
        "message": f"Product added {product.name}",
        "products": products
    }

@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product.id == product_id:
            return product

    raise HTTPException(status_code=404, detail="Product not found")


@app.put("/products/{product_id}")

def update_product(product_id: int, updated_product: Product):

    for index, product in enumerate(products):
        if product.id == product_id:
            products[index] = updated_product

            return updated_product


    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    for index,product in enumerate(products):
        if product.id == product_id:
            products.pop(index)


            return{
                "message": f"Product {product.name} deleted",
                "products": products
            }
    raise HTTPException(status_code=404, detail="Product not found")



# app = FastAPI()
# @app.get("/")
# def home():
#     return {"Hello": "World"}


