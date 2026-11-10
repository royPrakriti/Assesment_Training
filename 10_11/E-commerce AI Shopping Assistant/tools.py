
import json
from pathlib import Path
from agent_framework import tool

DATA_FILE = Path(__file__).parent / "products.json"


def load_products():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# Tool 1: Search Products
@tool(approval_mode="never_require")
def search_products(query: str) -> str:
    """Search products by product name or category."""

    print(f"\n[TOOL CALLED] search_products: {query}")

    if not query or not query.strip():
        return "Please provide a product name or category."

    products = load_products()

    matches = [
        p for p in products
        if query.lower() in p["name"].lower()
        or query.lower() in p["category"].lower()
    ]

    if not matches:
        return f"No products found matching '{query}'."

    results = [
        {
            "id": p["id"],
            "name": p["name"],
            "category": p["category"],
            "price_inr": p["price_inr"],
            "stock": p["stock"],
            "rating": p["rating"]
        }
        for p in matches
    ]

    return json.dumps(results, indent=4)


# Tool 2: Calculate Order Total
@tool(approval_mode="never_require")
def calculate_order_total(product_id: str, quantity: int) -> str:
    """Calculate total order cost and validate available stock."""

    print(
        f"\n[TOOL CALLED] calculate_order_total: "
        f"{product_id}, {quantity}"
    )

    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity < 1
    ):
        return "Invalid quantity. Quantity must be a positive integer."

    products = load_products()

    for p in products:

        if p["id"].upper() == product_id.strip().upper():

            available_stock = p["stock"]
            price = p["price_inr"]

            if quantity > available_stock:
                return json.dumps({
                    "id": p["id"],
                    "product_name": p["name"],
                    "requested_quantity": quantity,
                    "available_stock": available_stock,
                    "status": "Insufficient stock"
                }, indent=4)

            total = price * quantity

            return json.dumps({
                "id": p["id"],
                "product_name": p["name"],
                "quantity": quantity,
                "price_per_unit": price,
                "total_cost": total,
                "currency": "INR",
                "remaining_stock": available_stock - quantity,
                "status": "Success"
            }, indent=4)

    return f"Product with ID '{product_id}' does not exist."
