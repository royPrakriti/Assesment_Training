from fastapi import FastAPI

app = FastAPI()


class Product(BaseModel):
    name: str
    price: float


products = []

@app.get("/")
def home():
    return {"message": "Hello from FastAPI"}


@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/products")
def get_products():
    return products
