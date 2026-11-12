# from flask import Flask
# from flask import jsonify,request
#
#
#
# app = Flask(__name__)
#
#
#
#
# students = [
# {
# "id": 1,
# "name": "Rhea Kapoor",
# "course": "Python",
# "score": 82
# },
# {
# "id": 2,
# "name": "Zain Malik",
# "course": "SQL",
# "score": 76
# },
# {
# "id": 3,
# "name": "Devika Rao",
# "course": "Cloud",
# "score": 91
# }
# ]
#
# @app.route("/students",
# methods = ["GET"])
# def get_students():
#     return jsonify(students)
#
#
# @app.route("/students/<int:id>",
# methods = ["GET"])
# def get_student(id):
#     for student in students:
#         if student["id"] == id:
#             return jsonify(student)
#
#
#     return jsonify({"message": "Student not found"}),404
#
# @app.route("/students",
# methods = ["POST"])
# def add_student():
#     data = request.get_json()
#     students.append(data)
#
#     return jsonify({"message": "Student added"},
#                    {"student" : data}), 201
#
# @app.route("/students/<int:id>",methods = ["PUT"])
# def update_student(id):
#     data = request.get_json()
#     for student in students:
#         if student["id"] == id:
#             student.update(data)
#             return jsonify({"message": "Student updated"}),200
#     return jsonify({"message": "Student not found"}),404
#
# @app.route("/students/delete/<int:id>",
# methods = ['DELETE'])
# def delete_student(id):
#     for student in students:
#         if student["id"] == id:
#             students.remove(student)
#
#             return jsonify({"message": "Student deleted"})
#
#     return jsonify({"message": "Student not found"}),404
#
# if __name__ == '__main__':
#     app.run(debug=True)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()


# Enable CORS for React/Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Product model
class Product(BaseModel):
    id: int
    name: str
    price: float
    image: str


# In-memory product data
products = [
    {
        "id": 1,
        "name": "Wireless Headphones",
        "price": 4500,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e"
    },
    {
        "id": 2,
        "name": "Smart Watch",
        "price": 7000,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30"
    },
    {
        "id": 3,
        "name": "Laptop",
        "price": 65000,
        "image": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853"
    }
]


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Product API is running"
    }


# GET all products
@app.get("/products")
def get_products():
    return products


# GET product by ID
@app.get("/products/{product_id}")
def get_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


# POST - Add product
@app.post("/products")
def add_product(product: Product):

    for existing_product in products:
        if existing_product["id"] == product.id:
            raise HTTPException(
                status_code=400,
                detail="Product ID already exists"
            )

    products.append(product.model_dump())

    return {
        "message": "Product added successfully",
        "product": product
    }


# PUT - Update product
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    updated_product: Product
):

    for index, product in enumerate(products):

        if product["id"] == product_id:

            products[index] = updated_product.model_dump()

            return {
                "message": "Product updated successfully",
                "product": updated_product
            }

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


# DELETE - Delete product
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for index, product in enumerate(products):

        if product["id"] == product_id:

            deleted_product = products.pop(index)

            return {
                "message": "Product deleted successfully",
                "product": deleted_product
            }

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )