
import json
from pathlib import Path
from langchain.tools import tool
from guardrails import validate_guest_count

# Load restaurants.json from the same directory
DATA_FILE = Path(__file__).parent / "restaurants.json"


def load_restaurants():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# TOOL 1: Search Restaurants
@tool
def search_restaurants(keyword: str) -> str:
    """
    Search restaurants by cuisine type or restaurant name.
    Return matching restaurants with prices and available seats.
    """
    restaurants = load_restaurants()

    keyword = keyword.strip().lower()

    matches = [
        restaurant for restaurant in restaurants
        if keyword in restaurant["cuisine"].lower()
        or keyword in restaurant["name"].lower()
    ]

    if not matches:
        return f"No restaurants found for '{keyword}'."

    result = "Matching Restaurants:\n\n"

    for restaurant in matches:
        result += (
            f"Restaurant ID: {restaurant['id']}\n"
            f"Name: {restaurant['name']}\n"
            f"Cuisine: {restaurant['cuisine']}\n"
            f"Location: {restaurant['location']}\n"
            f"Price per person: ₹{restaurant['price_per_person']}\n"
            f"Available seats: {restaurant['available_seats']}\n"
            f"{'-' * 35}\n"
        )

    return result


# TOOL 2: Calculate Dining Cost
@tool
def calculate_dining_cost(
    restaurant_id: str,
    number_of_guests: int
) -> str:
    """
    Calculate estimated dining cost using restaurant ID
    and number of guests.
    """

    is_valid, error_message = validate_guest_count(number_of_guests)

    if not is_valid:
        return error_message

    if number_of_guests <= 0:
        return "Number of guests must be greater than zero."

    restaurants = load_restaurants()

    restaurant = next(
        (
            r for r in restaurants
            if r["id"].lower() == restaurant_id.strip().lower()
        ),
        None
    )

    if restaurant is None:
        return f"Restaurant with ID '{restaurant_id}' does not exist."

    price = restaurant["price_per_person"]
    total_cost = price * number_of_guests

    return (
        f"Dining Cost Estimate\n"
        f"Restaurant: {restaurant['name']}\n"
        f"Restaurant ID: {restaurant['id']}\n"
        f"Price per person: ₹{price}\n"
        f"Number of guests: {number_of_guests}\n"
        f"Total estimated cost: ₹{total_cost}"
    )
