
import os
import json
from groq import Groq
from dotenv import load_dotenv

from tools import search_books, reserve_book

# Load environment variables
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "llama-3.3-70b-versatile"
)


# Define tools for Groq Function Calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_books",
            "description": "Search books by title, keyword, author, or category and return matching books with availability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Book title, keyword, author, or category"
                    }
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reserve_book",
            "description": "Reserve a book using its ID and customer name. Checks availability and asks for confirmation before saving.",
            "parameters": {
                "type": "object",
                "properties": {
                    "book_id": {
                        "type": "integer",
                        "description": "Unique book ID"
                    },
                    "customer_name": {
                        "type": "string",
                        "description": "Customer name"
                    }
                },
                "required": ["book_id", "customer_name"]
            }
        }
    }
]


# Map tool names to Python functions
available_functions = {
    "search_books": search_books,
    "reserve_book": reserve_book
}


def library_agent():

    print("\n===================================")
    print("       LIBRARY AI AGENT")
    print("       Powered by Groq Llama")
    print("===================================")

    messages = [
        {
            "role": "system",
            "content": """
            You are a helpful Library AI Assistant.

            You can search books and reserve books using Python tools.

            Rules:
            1. Use search_books for book searches and availability.
            2. Use reserve_book when a user requests a reservation.
            3. Ask for missing book ID or customer name.
            4. Never claim a reservation is successful unless the
               Python tool confirms it.
            5. Never invent book details or availability.
            6. Explain results clearly.
            """
        }
    ]

    while True:

        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nLibrary Agent: Thank you for visiting!")
            break

        if not user_input:
            continue

        messages.append({
            "role": "user",
            "content": user_input
        })

        try:

            # Send request to Groq model
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message

            # Execute tools selected by the model
            while assistant_message.tool_calls:

                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        tool_call.model_dump()
                        for tool_call in assistant_message.tool_calls
                    ]
                })

                for tool_call in assistant_message.tool_calls:

                    function_name = tool_call.function.name

                    function_args = json.loads(
                        tool_call.function.arguments
                    )

                    # Display selected tool
                    print(
                        f"\n[AI AGENT] Selected Tool: {function_name}"
                    )
                    print(
                        f"[AI AGENT] Arguments: {function_args}"
                    )

                    # Execute Python function
                    function_to_call = available_functions.get(
                        function_name
                    )

                    if function_to_call is None:
                        tool_result = {
                            "success": False,
                            "message": "Unknown tool."
                        }
                    else:
                        try:
                            tool_result = function_to_call(
                                **function_args
                            )

                        except Exception as error:
                            tool_result = {
                                "success": False,
                                "message": str(error)
                            }

                    # Return tool result to Groq
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(
                            tool_result,
                            default=str
                        )
                    })

                # Ask model to process tool results
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto"
                )

                assistant_message = response.choices[0].message

            # Display final AI response
            final_answer = assistant_message.content or ""

            messages.append({
                "role": "assistant",
                "content": final_answer
            })

            print("\nLibrary Agent:", final_answer)

        except Exception as error:
            print("\nError:", str(error))


if __name__ == "__main__":
    library_agent()
