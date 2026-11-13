import json
from pathlib import Path
from langchain.tools import tool

FILE = Path(__file__).parent / "workshops.json"


def get_workshops():
    return json.loads(FILE.read_text(encoding="utf-8"))


@tool
def search_workshops(keyword: str) -> str:
    """Search available workshops by title."""

    matches = [
        w for w in get_workshops()
        if keyword.lower() in w["title"].lower()
    ]

    return json.dumps(matches)


@tool
def calculate_workshop_fee(
    workshop_id: str,
    participants: int
) -> str:
    """Calculate the total fee for a workshop and participant count."""
    if participants < 1 or participants > 30:
        return "Participant count must be between 1 and 30."
    
    for workshop in get_workshops():

        if workshop["id"] == workshop_id:
            total = workshop["fee"] * participants

            return json.dumps({
                "workshop": workshop["title"],
                "participants": participants,
                "total_fee": total
            })

    return "Workshop not found."

@tool
def list_all_workshops() -> str:
    """List all workshops."""
    return json.dumps(get_workshops())

@tool
def find_cheapest_workshop(
) -> dict:
    """Find the cheapest workshop."""
    workshops = get_workshops()

    if not workshops:
        return {"error": "No workshops available."}

    cheapest = workshops[0]

    for workshop in workshops:
        if workshop["fee"] < cheapest["fee"]:
            cheapest = workshop

    return cheapest

# Load coupon data
def load_coupons():
    with open("coupon_codes.json", "r") as file:
        data = json.load(file)

    return data["coupons"]


# Coupon discount logic
@tool
def apply_workshop_coupon(
    price: float,
    coupon_code: str,
    booking_type: str
) -> dict:
    """Validate coupon code and calculate workshop discount."""

if __name__ == "__main__":
    print(search_workshops.invoke({"keyword": "Python"}))

    print(calculate_workshop_fee.invoke({
        "workshop_id": "W101",
        "participants": 4
    }))
