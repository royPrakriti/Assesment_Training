import json
from fileinput import filename
from typing import Literal

from pydantic import BaseModel, ValidationError, Field
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
    filename = "registration.log",
    filemode = "a"
)

# Pydantic model
class Registration(BaseModel):
    registration_id: str
    name: str
    age: int = Field(gt=18)
    email: str
    ticket_type: Literal["Standard","Premium","VIP"]
    amount: float = Field(gt=500)

with open("registrations.json") as file:
    data = json.load(file)

validate_records = []
for item in data:
    try:
        valid_registration = Registration(**item)
        validate_records.append(valid_registration.model_dump())

        if valid_registration.ticket_type == "VIP":
            logging.warning("VIP Ticket detected")

        print(valid_registration.model_dump())
        logging.info(f"Registration of {item.get('registration_id')} is validated")


    except ValidationError as e:
        logging.error(f"Invalid registration data: {item.get('registration_id')}")
        print(e)


with open("validate_records.json", "w") as file:
    json.dump(validate_records, file)