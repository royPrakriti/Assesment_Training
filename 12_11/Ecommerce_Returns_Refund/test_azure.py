
import os
import asyncio
from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

load_dotenv()


async def main():

    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    base_url = os.getenv("AZURE_OPENAI_BASE_URL")
    model = os.getenv("AZURE_OPENAI_MODEL")

    if not api_key or not base_url or not model:
        raise ValueError("Azure OpenAI configuration is missing!")

    client = OpenAIChatClient(
        model=model,
        base_url=base_url,
        api_key=api_key
    )

    agent = Agent(
        client=client,
        name="ConnectionTestAgent",
        instructions="You are a helpful AI assistant."
    )

    response = await agent.run(
        "Explain e-commerce returns processing in two sentences."
    )

    print("\nAzure OpenAI Connection Successful!")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
