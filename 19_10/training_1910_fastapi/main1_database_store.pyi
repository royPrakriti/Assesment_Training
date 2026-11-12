from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
app = FastAPI()

class Product(BaseModel):
    id: int
    name: str
    price: float


def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="fastapi_store",
        port=5432,
        user="postgres",
        password="Admin@123",
    )

    return conn


@app.get("/products")
def get_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM product")
    products = cur.fetchall()
    return products

@app.post("/products")
def add_product(product: Product):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO product (id, name, price)
    VALUES (%s, %s, %s)
    """, (product.id, product.name, product.price)
                )
    conn.commit()
    cur.close()
    conn.close()

