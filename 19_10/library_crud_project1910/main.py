from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
app = FastAPI()

class Book(BaseModel):
    book_id: int
    title: str
    author: str
    category: str
    price: float
    stock: int

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="library_store",
        port=5432,
        user="postgres",
        password="Admin@123",
    )

    return conn

@app.post("/books/inserting")
def insert_book(book: Book):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO books (book_id, title, author, category, price, stock)
    VALUES (%s, %s, %s, %s, %s, %s)""",
    (book.book_id, book.title,book.author,book.category,book.price,book.stock))



    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Book inserted successfully"}
    
    
    
@app.get("/books")
def get_books():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books")
    books = cur.fetchall()
    cur.close()
    conn.close()
    return books
    
@app.get("/books/category/{category}")

def get_category(category: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books WHERE category = %s", (category,))
    books = cur.fetchall()

    cur.close()
    conn.close()
    return books


@app.get("/books/price/{price}")
def get_products(price: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM product WHERE price > %s", (price,))
    books = cur.fetchall()
    return books
    conn.commit()
    conn.close()
@app.put("/books/{book_id}/{price}")
def update_price_book(book_id: int, price: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE books SET price = %s WHERE book_id = %s", (price, book_id))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    cur.close()


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
    result = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()


@app.get("/books/highest_price")
def get_highest_price():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books ORDER BY price DESC limit 1")
    result = cur.fetchone()
    conn.commit()
    conn.close()
    cur.close()


@app.get("/books/total_stock")
def get_total_stock():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(stock) FROM books")
    total_stock = cur.fetchone()
    conn.commit()
    conn.close()
    cur.close()

@app.get("/books/count_by_category")
def count_by_category():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT category, COUNT(*) FROM books GROUP BY category")
    result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
