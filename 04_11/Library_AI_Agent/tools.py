
import json
from pathlib import Path
from datetime import datetime
import uuid

# Get project directory
BASE_DIR = Path(__file__).resolve().parent

BOOKS_FILE = BASE_DIR / "books.json"
RESERVATIONS_FILE = BASE_DIR / "reservations.json"


def load_books():
    """Load books from books.json."""
    with open(BOOKS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_books(books):
    """Save updated books into books.json."""
    with open(BOOKS_FILE, "w", encoding="utf-8") as file:
        json.dump(books, file, indent=4)


def load_reservations():
    """Load reservations from reservations.json."""
    if not RESERVATIONS_FILE.exists():
        return []

    with open(RESERVATIONS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_reservations(reservations):
    """Save reservations into reservations.json."""
    with open(RESERVATIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(reservations, file, indent=4)


# TOOL 1: SEARCH BOOKS

def search_books(keyword):
    """
    Search books by title, author, or category.
    Returns matching books and their availability.
    """

    books = load_books()
    keyword = keyword.strip().lower()

    if not keyword:
        return []

    matching_books = []

    for book in books:
        if (
            keyword in book["title"].lower()
            or keyword in book["author"].lower()
            or keyword in book["category"].lower()
        ):
            matching_books.append({
                "id": book["id"],
                "title": book["title"],
                "author": book["author"],
                "category": book["category"],
                "available_copies": book["available_copies"],
                "availability": (
                    "Available"
                    if book["available_copies"] > 0
                    else "Not Available"
                )
            })

    return matching_books


# TOOL 2: RESERVE BOOK

def reserve_book(book_id, customer_name):
    """
    Reserve a book if copies are available.
    Ask for customer confirmation before reservation.
    Update books.json and reservations.json.
    """

    books = load_books()

    # Find requested book
    selected_book = None

    for book in books:
        if book["id"] == book_id:
            selected_book = book
            break

    # Check if book exists
    if selected_book is None:
        return {"success": False, "message": "Book ID not found."}

    # Check availability
    if selected_book["available_copies"] <= 0:
        return {
            "success": False,
            "message": f"Sorry, '{selected_book['title']}' is out of stock."
        }

    # Validate customer name
    customer_name = customer_name.strip()

    if not customer_name:
        return {"success": False, "message": "Customer name is required."}

    # Ask for confirmation
    print(f"\nBook: {selected_book['title']}")
    print(f"Customer: {customer_name}")
    print(f"Available copies: {selected_book['available_copies']}")

    confirmation = input(
        "\nDo you want to confirm this reservation? (yes/no): "
    ).strip().lower()

    if confirmation not in ("yes", "y"):
        return {
            "success": False,
            "message": "Reservation cancelled by customer."
        }

    # Create reservation
    reservation = {
        "reservation_id": str(uuid.uuid4()),
        "book_id": selected_book["id"],
        "book_title": selected_book["title"],
        "customer_name": customer_name,
        "reservation_date": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "status": "Confirmed"
    }

    # Load existing reservations
    reservations = load_reservations()

    # Reduce available copies
    selected_book["available_copies"] -= 1

    # Save updated data
    save_books(books)

    reservations.append(reservation)
    save_reservations(reservations)

    return {
        "success": True,
        "message": "Book reserved successfully!",
        "reservation_details": reservation,
        "remaining_copies": selected_book["available_copies"]
    }
