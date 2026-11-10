
import re


# 1. Input validation
def validate_input(user_input: str) -> tuple[bool, str]:

    if not user_input or not user_input.strip():
        return False, "Please enter a question."

    if len(user_input) > 500:
        return False, "Your question is too long. Maximum length is 500 characters."

    return True, ""

def detect_pii(text: str) -> bool:

    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    phone_pattern = r"(?<!\w)(?:\+91[\s-]?)?[6-9]\d{9}(?!\w)"

    email_found = re.search(email_pattern, text)
    phone_found = re.search(phone_pattern, text)

    return bool(email_found or phone_found)


# 5. PII redaction
def redact_pii(text: str) -> str:

    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    phone_pattern = r"(?<!\w)(?:\+91[\s-]?)?[6-9]\d{9}(?!\w)"

    text = re.sub(email_pattern, "[EMAIL REDACTED]", text)

    text = re.sub(phone_pattern, "[PHONE REDACTED]", text)

    return text


# 6. Input PII masking
def sanitize_input(text: str) -> str:

    return redact_pii(text)

# 2. Domain restriction
def is_restaurant_related(user_input: str, has_context=False) -> bool:

    text = user_input.lower().strip()

    restaurant_keywords = [
        "restaurant", "restaurants", "food", "cuisine",
        "indian", "italian", "japanese", "mexican",
        "american", "seafood", "chinese", "thai",
        "spice garden", "olive", "sakura", "coastal",
        "taco", "smokehouse",
        "dining", "dinner", "lunch", "meal",
        "price", "cost", "budget", "bill",
        "guest", "guests", "people", "seats",
        "available", "availability", "booking",
        "reservation", "restaurant id",
        "R101", "R102", "R103", "R104", "R105", "R106"
    ]

    # Allow short follow-up messages when conversation context exists
    follow_up_pattern = (
        r"^(yes|no|ok|okay|sure|"
        r"\d+\s*(people|person|persons|guests)?|"
        r"what about \d+|"
        r"for \d+|"
        r"same|that one|previous one)$"
    )

    if has_context and re.match(follow_up_pattern, text):
        return True

    return any(keyword in text for keyword in restaurant_keywords)


# 3. Tool validation
def validate_guest_count(number_of_guests: int) -> tuple[bool, str]:

    if not isinstance(number_of_guests, int) or isinstance(number_of_guests, bool):
        return False, "Guest count must be a whole number."

    if number_of_guests < 1:
        return False, "At least 1 guest is required."

    if number_of_guests > 20:
        return False, "A maximum of 20 guests is allowed."

    return True, ""


