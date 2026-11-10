
import asyncio

from dotenv import load_dotenv

from agent_framework import AgentResponse
from agent_framework.orchestrations import SequentialBuilder

from agents import create_agents


# Load environment variables
load_dotenv()


async def main():

    # Step 1: Create all three agents
    (
        inventory_agent,
        pricing_agent,
        recommendation_agent
    ) = create_agents()

    # Step 2: Build sequential workflow
    workflow = SequentialBuilder(
        participants=[
            inventory_agent,
            pricing_agent,
            recommendation_agent
        ],
        output_from="all"
    ).build()

    # Step 3: Get customer request
    question = input("\nCustomer: ").strip()

    if not question:
        print("Please enter a valid product request.")
        return

    # Step 4: Execute workflow asynchronously
    print("\nStarting Product Recommendation Workflow...\n")

    result = await workflow.run(question)

    # Step 5: Collect agent outputs
    outputs = result.get_outputs()

    if not outputs:
        print("No response was generated.")
        return

    # Step 6: Display intermediate agent results
    for index, output in enumerate(outputs[:-1], start=1):

        if isinstance(output, AgentResponse):

            if index == 1:
                agent_name = "Inventory Agent"

            elif index == 2:
                agent_name = "Pricing Agent"

            else:
                agent_name = "Agent"

            print("\n" + "=" * 60)
            print(f" {agent_name} - Intermediate Result")
            print("=" * 60)

            for message in output.messages:
                if message.text:
                    print(message.text)

    # Step 7: Display final recommendation
    final_output = outputs[-1]

    print("\n" + "=" * 60)
    print(" FINAL PRODUCT RECOMMENDATION")
    print("=" * 60)

    if isinstance(final_output, AgentResponse):

        for message in final_output.messages:
            if message.text:
                print(message.text)


if __name__ == "__main__":
    asyncio.run(main())
