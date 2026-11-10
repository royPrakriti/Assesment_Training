
import os

from agent_framework import Agent
from agent_framework.openai import OpenAIChatCompletionClient

from tools import search_products, calculate_order_total


def create_agents():

    # Shared Groq model client
    client = OpenAIChatCompletionClient(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1"
    )

    # GPT-OSS 20B does not support parallel tool calls on Groq.
    client.function_invocation_configuration[
        "allow_concurrent_invocation"
    ] = False

    # --------------------------------------------------
    # Agent 1: Inventory Agent
    # --------------------------------------------------

    inventory_agent = Agent(
        client=client,
        name="InventoryAgent",

        instructions=(
            "You are a Product Inventory Specialist. "

            "Understand the customer's product requirements. "

            "Use search_products to search the product dataset. "

            "Search using the relevant product name or category. "

            "Identify matching products and provide their "
            "ID, name, category, price, stock and rating. "

            "Never invent product information. "

            "Clearly identify unavailable products. "

            "Pass all relevant inventory information "
            "to the Pricing Agent."
        ),

        tools=[search_products]
    )

    # --------------------------------------------------
    # Agent 2: Pricing Agent
    # --------------------------------------------------

    pricing_agent = Agent(
        client=client,
        name="PricingAgent",

        instructions=(
            "You are a Product Pricing Specialist. "

            "Review the inventory results and original customer request. "

            "Identify the quantity requested by the customer. "

            "If no quantity is specified, use quantity 1 "
            "and clearly state this assumption. "

            "For every matching product, call "
            "calculate_order_total exactly once. "

            "Use the product ID from the JSON field named 'id'. "

            "Pass the requested quantity to the tool. "

            "Call the tool for each matching product separately. "

            "Do not repeat a calculation that has already succeeded. "

            "Wait for the tool results before preparing your analysis. "

            "Compare the verified total cost against the customer's "
            "budget, if a budget was specified. "

            "Clearly identify insufficient stock and products "
            "that exceed the budget. "

            "Never invent prices, stock quantities or totals. "

            "Return the calculation results and pricing analysis "
            "to the Recommendation Agent."
        ),

        tools=[calculate_order_total]
    )

    # --------------------------------------------------
    # Agent 3: Recommendation Agent
    # --------------------------------------------------

    recommendation_agent = Agent(
        client=client,
        name="RecommendationAgent",

        instructions=(
            "You are a Product Recommendation Specialist. "

            "Review the original customer request, inventory results "
            "and pricing results from the previous agents. "

            "Recommend the highest-rated product that satisfies "
            "the customer's budget and requested quantity. "

            "Only consider products with sufficient stock "
            "and successfully verified order totals. "

            "If multiple products have the same rating, "
            "prefer the product with the lower total cost. "

            "Never recommend unavailable or unaffordable products. "

            "Never invent product information. "

            "Provide the recommended product's name, ID, category, "
            "rating, unit price, quantity and total cost. "

            "Explain briefly why the product was selected. "

            "If no product satisfies the requirements, "
            "clearly explain why."
        )
    )

    return (
        inventory_agent,
        pricing_agent,
        recommendation_agent
    )
