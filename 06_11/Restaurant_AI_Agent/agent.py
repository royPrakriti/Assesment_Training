
import uuid

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from tools import search_restaurants, calculate_dining_cost

from guardrails import (
    validate_input,
    is_restaurant_related,
    detect_pii,
    sanitize_input,
    redact_pii
)

load_dotenv()

# Initialize Groq model
model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

# Register tools
tools = [
    search_restaurants,
    calculate_dining_cost
]

# Initialize memory
memory = InMemorySaver()

# Create agent
agent = create_agent(
    model=model,
    tools=tools,
    checkpointer=memory,
    system_prompt=(
        "You are a Restaurant AI Assistant. "

        "STRICT DOMAIN RESTRICTION: "
        "Only answer questions related to restaurants, "
        "cuisines, restaurant searches and dining costs. "

        "Use search_restaurants to search for restaurants. "
        "Use calculate_dining_cost to calculate dining costs. "

        "CONVERSATION MEMORY: "
        "Remember previously selected restaurants, "
        "restaurant IDs, guest counts and dining calculations. "
        "Understand short follow-up messages using conversation history. "

        "GUEST VALIDATION: "
        "Guest counts must be between 1 and 20. "

        "ACCURACY RULES: "
        "Never invent restaurant names, prices, locations "
        "or seating availability. "
        "Always use the registered tools for restaurant information "
        "and dining cost calculations. "
        "Only provide information returned by the tools. "

        "If a restaurant does not exist, communicate that clearly. "
        "If information is missing, ask the user for clarification. "

        "For unrelated questions, respond: "
        "'I can only help with restaurant-related questions.'"
    )
)

# Conversation ID
thread_id = str(uuid.uuid4())

# Track whether conversation context exists
has_context = False

print("\n===== RESTAURANT AI ASSISTANT =====")
print("Guardrails and conversation memory enabled.")
print("Type /new to start a fresh conversation.")
print("Type exit to quit.\n")


while True:

    user_input = input("You: ").strip()

    # Exit
    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    # New conversation
    if user_input.lower() == "/new":

        thread_id = str(uuid.uuid4())
        has_context = False

        print("\nNew conversation started!\n")
        continue

    # Guardrail 1: Input validation
    is_valid, error_message = validate_input(user_input)

    if not is_valid:
        print("\nGuardrail:", error_message, "\n")
        continue

    # Guardrail 2: PII Detection
    if detect_pii(user_input):
        print("\nGuardrail: Personal information detected.")

        user_input = sanitize_input(user_input)

        print("Redacted Input:", user_input)

        print(
            "Guardrail: PII has been redacted. "
            "Please avoid sharing personal information.\n"
        )

        continue

    # Guardrail 3: Domain Restriction
    if not is_restaurant_related(user_input, has_context):
        print(
            "\nGuardrail: I can only help with "
            "restaurant-related questions.\n"
        )

        continue

    # Memory configuration
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    try:

        # Invoke agent
        response = agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": user_input}
                ]
            },
            config=config
        )

        has_context = True

        # Print tool execution details
        print("\n--- TOOL EXECUTION DETAILS ---")

        tool_found = False

        for message in response["messages"]:

            if getattr(message, "tool_calls", None):

                for tool_call in message.tool_calls:

                    tool_found = True

                    print("Selected Tool:", tool_call["name"])
                    print("Arguments:", tool_call["args"])

        if not tool_found:
            print("No tool executed.")

        # Display final response
        print("\n--- AI RESPONSE ---")

        final_message = response["messages"][-1]

        final_response = final_message.content

        # Guardrail 4: Output PII redaction
        final_response = redact_pii(final_response)

        print(final_response)

    except Exception as e:

        print("\nError:", str(e))

    print("\n" + "=" * 45 + "\n")
