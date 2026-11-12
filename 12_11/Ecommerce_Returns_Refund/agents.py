
import os
from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

load_dotenv()


# ==========================================
# AZURE OPENAI CLIENT
# ==========================================

def create_model_client():

    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    base_url = os.getenv("AZURE_OPENAI_BASE_URL")
    model = os.getenv("AZURE_OPENAI_MODEL")

    if not api_key or not base_url or not model:
        raise ValueError(
            "Missing Azure OpenAI configuration in .env"
        )

    return OpenAIChatClient(
        model=model,
        base_url=base_url,
        api_key=api_key
    )


# ==========================================
# AGENT 1: ELIGIBILITY AGENT
# ==========================================

def create_eligibility_agent(client):

    return Agent(
        client=client,
        name="EligibilityAgent",
        instructions="""
        You are an E-commerce Return Eligibility Specialist.

        Analyze customer return requests using the company's
        return policy.

        Evaluate:

        1. Product amount must be below Rs. 25,000.
        2. Request must be within 30 days of delivery.
        3. Customer invoice must be available.
        4. Item must be unopened OR damaged with supporting photos.
        5. Previous returns must be fewer than 3 within 90 days.

        Identify:
        - Conditions satisfied.
        - Conditions failed.
        - Eligibility exceptions.
        - Explanation of findings.

        Never make the final approval decision.
        Python business rules determine the final decision.
        Never invent missing information.
        """
    )


# ==========================================
# AGENT 2: RISK AGENT
# ==========================================

def create_risk_agent(client):

    return Agent(
        client=client,
        name="RiskAgent",
        instructions="""
        You are an E-commerce Return Risk Assessment Specialist.

        Analyze return requests for:

        1. High-value products.
        2. Frequent customer returns.
        3. Missing invoice.
        4. Missing damage photographs.
        5. Suspicious return reasons.
        6. Inconsistent request information.

        Assign a risk level:

        LOW - No significant risk.
        MEDIUM - Some concerns require attention.
        HIGH - Significant concerns requiring human review.

        Return:
        - Risk level.
        - Risk factors.
        - Explanation.
        - Recommended action.

        Never approve or reject a request yourself.
        Never invent customer information.
        """
    )


# ==========================================
# AGENT 3: CUSTOMER RESPONSE AGENT
# ==========================================

def create_customer_response_agent(client):

    return Agent(
        client=client,
        name="CustomerResponseAgent",
        instructions="""
        You are a professional E-commerce Customer Support Agent.

        Generate customer-facing messages using the final
        workflow decision.

        Possible decisions:

        AUTO_APPROVED:
        Communicate automatic approval.

        MANAGER_APPROVED:
        Communicate approval after manager review.

        MANAGER_REJECTED:
        Politely communicate rejection following manager review.

        PENDING_HUMAN_REVIEW:
        Inform the customer that the request is under review.

        Important rules:

        - Never claim that a refund has been processed.
        - Never claim that a replacement has been shipped.
        - Never contradict the manager's decision.
        - Never invent transaction details or dates.
        - Keep messages professional and concise.
        """
    )


# ==========================================
# CREATE ALL AGENTS
# ==========================================

def create_agents():

    client = create_model_client()

    eligibility_agent = create_eligibility_agent(client)
    risk_agent = create_risk_agent(client)
    customer_response_agent = create_customer_response_agent(client)

    return (
        eligibility_agent,
        risk_agent,
        customer_response_agent
    )
