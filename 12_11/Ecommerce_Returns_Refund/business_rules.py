
# ==========================================
# BUSINESS RULES
# ==========================================

def check_eligibility(request):
    """
    Validate a return request against fixed business rules.
    """

    issues = []

    # Rule 1: Return amount must be below Rs. 25,000
    if request["amount_inr"] >= 25000:
        issues.append("Amount exceeds the Rs. 25,000 limit")

    # Rule 2: Return must be requested within 30 days
    if request["days_since_delivery"] > 30:
        issues.append("Return period exceeds 30 days")

    # Rule 3: Invoice must be available
    if not request["invoice_available"]:
        issues.append("Invoice is missing")

    # Rule 4: Item must be unopened or damaged with photos
    condition = request["item_condition"].upper()

    if condition == "DAMAGED":
        if not request["photo_evidence_available"]:
            issues.append("Damage photographs are missing")

    elif condition != "UNOPENED":
        issues.append("Item condition is not acceptable")

    # Rule 5: Maximum 2 previous returns in 90 days
    if request["previous_returns_90_days"] >= 3:
        issues.append("Customer has reached the return limit")

    return issues


def get_risk_level(risk_text):
    """
    Extract the risk level from the Risk Agent response.
    """

    import re

    normalized = risk_text.replace("*", "").replace("#", "").upper()

    match = re.search(
        r"RISK LEVEL\s*:\s*(LOW|MEDIUM|HIGH)\b",
        normalized
    )

    # Treat unclear risk assessments as HIGH risk
    return match.group(1) if match else "HIGH"


def determine_approval_route(issues, risk_level):
    """
    Decide whether the request can be auto-approved
    or requires manager approval.
    """

    if issues or risk_level == "HIGH":
        return "Human Review"

    return "Automatic"
