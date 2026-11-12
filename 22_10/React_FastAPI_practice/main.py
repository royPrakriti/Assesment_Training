import psycopg2
from fastapi import FastAPI
from fastapi.middleware import cors
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    cors.CORSMiddleware,

    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Product(BaseModel):
    id: int
    name: str
    price: float
    image: str





def get_connection():
    return psycopg2.connect(
            host="localhost",
            database="product_store",
            user="postgres",
            password="Admin@123"
    )


@app.get("/products")
def get_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
            SELECT id, name, price, image
            FROM products
            ORDER BY id
        """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    products = []


    for row in rows:
        products.append({
            "id": row[0],
            "name": row[1],
            "price": float(row[2]),
            "image": row[3]
        })
    return products

@app.get("/products/{id}")
def get_product(id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(""" SELECT id, name, price, image FROM products WHERE id = %s """,(id,))
    row = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    if row is None:
        return {"message": "Product not found"},404

    return{
        "id": row[0],
        "name": row[1],
        "price": row[2],
        "image": row[3]
    }
@app.post("/products")
def add_product(product: Product):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   insert into products (id, name, price, image) values (%s, %s, %s, %s)
                   """,(product.id, product.name, product.price, product.image))
    row = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()

    print(row)

@app.put("/products/{id}")
def update_product(id: int, product: Product):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(""" UPDATE products SET name = %s, price = %s, image = %s WHERE id = %s """,(product.name, product.price, product.image, id))
    row = cursor.fetchone()

    if row:
        return {"message": "Product was successfully updated"}
    else:
        return {"message": "Product was not updated"},404

    conn.commit()
    cursor.close()
    conn.close()


@app.delete("/products/{id}")
def delete_product(id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(""" DELETE FROM products WHERE id = %s Returning id """,(id))

    row = cursor.fetchone()

    if row is None:
        return {"message": "Product not found"},404
    else:
        return {"message": "Product deleted"}

    conn.commit()
    cursor.close()
    conn.close()

