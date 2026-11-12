
import asyncio
import json

from agent_framework import (
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
    response_handler,
)

from agents import create_agents

from business_rules import (
    check_eligibility,
    get_risk_level,
    determine_approval_route,
)


# ==========================================
# MANAGER APPROVAL REQUEST
# ==========================================

class ManagerApprovalRequest:
    def __init__(self, request_id, product, amount,
                 eligibility_issues, risk_assessment, state):

        self.request_id = request_id
        self.product = product
        self.amount = amount
        self.eligibility_issues = eligibility_issues
        self.risk_assessment = risk_assessment
        self.state = state


# ==========================================
# 1. ELIGIBILITY EXECUTOR
# ==========================================

class EligibilityExecutor(Executor):

    def __init__(self, agent):
        super().__init__(id="eligibility_executor")
        self.agent = agent

    @handler
    async def process(self, request: dict, ctx: WorkflowContext):

        print("\n[Eligibility] Reviewing request...")

        result = await self.agent.run(
            f"Evaluate this return request:\n"
            f"{json.dumps(request, indent=2)}"
        )

        state = {
            "request": request,
            "eligibility_findings": result.text,
            "risk_assessment": "",
            "risk_level": "",
            "eligibility_issues": [],
            "approval_route": "",
            "final_decision": "",
            "customer_message": "",
        }

        await ctx.send_message(state)


# ==========================================
# 2. RISK EXECUTOR
# ==========================================

class RiskExecutor(Executor):

    def __init__(self, agent):
        super().__init__(id="risk_executor")
        self.agent = agent

    @handler
    async def process(self, state: dict, ctx: WorkflowContext):

        print("[Risk] Assessing request...")

        result = await self.agent.run(
            f"Assess the risk of this return request.\n"
            f"Request:\n{json.dumps(state['request'], indent=2)}\n"
            f"Eligibility findings:\n{state['eligibility_findings']}"
        )

        state["risk_assessment"] = result.text
        state["risk_level"] = get_risk_level(result.text)

        print("[Risk] Risk level:", state["risk_level"])

        await ctx.send_message(state)


# ==========================================
# 3. APPROVAL GATEWAY + HUMAN REVIEW
# ==========================================

class ApprovalGatewayExecutor(Executor):

    def __init__(self):
        super().__init__(id="approval_gateway")

    @handler
    async def process(self, state: dict, ctx: WorkflowContext):

        request = state["request"]

        # Apply the business rules
        issues = check_eligibility(request)
        state["eligibility_issues"] = issues

        # Decide the approval route
        route = determine_approval_route(
            issues,
            state["risk_level"]
        )

        state["approval_route"] = route

        # Automatic approval
        if route == "Automatic":

            state["final_decision"] = "AUTO_APPROVED"

            print("[Approval] Automatically approved.")

            await ctx.send_message(state)
            return

        # Manager approval required
        state["final_decision"] = "PENDING_HUMAN_REVIEW"

        approval_request = ManagerApprovalRequest(
            request_id=request["request_id"],
            product=request["product"],
            amount=request["amount_inr"],
            eligibility_issues=issues,
            risk_assessment=state["risk_assessment"],
            state=state,
        )

        print("[Approval] Manager review required.")

        await ctx.request_info(
            request_data=approval_request,
            response_type=str,
        )

    # Resume workflow after manager decision
    @response_handler
    async def on_manager_response(
        self,
        original_request: ManagerApprovalRequest,
        manager_decision: str,
        ctx: WorkflowContext,
    ):

        decision = manager_decision.strip().lower()

        if decision == "approve":
            final_decision = "MANAGER_APPROVED"

        elif decision == "reject":
            final_decision = "MANAGER_REJECTED"

        else:
            raise ValueError("Enter approve or reject")

        state = original_request.state
        state["final_decision"] = final_decision

        print("[Manager] Decision:", final_decision)

        await ctx.send_message(state)


# ==========================================
# 4. CUSTOMER RESPONSE EXECUTOR
# ==========================================

class CustomerResponseExecutor(Executor):

    def __init__(self, agent):
        super().__init__(id="customer_response_executor")
        self.agent = agent

    @handler
    async def process(self, state: dict, ctx: WorkflowContext):

        print("[Customer Response] Preparing message...")

        result = await self.agent.run(
            f"Prepare a customer communication draft.\n"
            f"Request:\n{json.dumps(state['request'], indent=2)}\n"
            f"Final decision: {state['final_decision']}\n"
            f"Approval route: {state['approval_route']}\n"
            f"Eligibility findings: {state['eligibility_findings']}\n"
            f"Risk assessment: {state['risk_assessment']}\n\n"
            "Follow the final decision exactly. Do not claim that "
            "a refund has been processed or a replacement shipped."
        )

        state["customer_message"] = result.text
        request = state["request"]

        final_output = {
            "request_id": request["request_id"],
            "order_id": request["order_id"],
            "product": request["product"],
            "requested_amount": request["amount_inr"],
            "eligibility_findings": state["eligibility_findings"],
            "eligibility_issues": state["eligibility_issues"],
            "risk_assessment": state["risk_assessment"],
            "risk_level": state["risk_level"],
            "approval_route": state["approval_route"],
            "final_decision": state["final_decision"],
            "customer_communication_draft": state["customer_message"],
        }

        await ctx.yield_output(final_output)


# ==========================================
# BUILD GRAPH WORKFLOW
# ==========================================

def build_workflow():

    eligibility_agent, risk_agent, response_agent = create_agents()

    eligibility = EligibilityExecutor(eligibility_agent)
    risk = RiskExecutor(risk_agent)
    approval = ApprovalGatewayExecutor()
    customer_response = CustomerResponseExecutor(response_agent)

    workflow = (
        WorkflowBuilder(start_executor=eligibility)
        .add_chain([
            eligibility,
            risk,
            approval,
            customer_response,
        ])
        .build()
    )

    return workflow


# ==========================================
# RUN WORKFLOW WITH HUMAN APPROVAL
# ==========================================

async def run_workflow(workflow, request):

    stream = workflow.run(request, stream=True)

    while True:

        responses = {}

        async for event in stream:

            if event.type == "request_info":

                approval = event.data

                print("\n--- MANAGER APPROVAL REQUIRED ---")
                print("Request ID:", approval.request_id)
                print("Product:", approval.product)
                print("Amount: Rs.", approval.amount)

                print("\nEligibility Issues:")
                for issue in approval.eligibility_issues:
                    print("-", issue)

                print("\nRisk Assessment:")
                print(approval.risk_assessment)

                decision = input(
                    "\nEnter approve or reject: "
                ).strip().lower()

                while decision not in ("approve", "reject"):

                    print("Invalid decision. Try again.")

                    decision = input(
                        "Enter approve or reject: "
                    ).strip().lower()

                responses[event.request_id] = decision

            elif event.type == "output":

                print("\n--- FINAL WORKFLOW OUTPUT ---")

                print(
                    json.dumps(
                        event.data,
                        indent=2,
                        ensure_ascii=False,
                    )
                )

        if not responses:
            break

        print("\n[Workflow] Resuming...")

        stream = workflow.run(
            stream=True,
            responses=responses,
        )


# ==========================================
# MAIN APPLICATION
# ==========================================

async def main():

    try:
        with open("returns.json", "r", encoding="utf-8") as file:
            requests = json.load(file)

        print(f"Loaded {len(requests)} return requests.")

        workflow = build_workflow()

        for request in requests:

            print(f"\n{'=' * 50}")
            print("Processing:", request["request_id"])
            print(f"{'=' * 50}")

            await run_workflow(workflow, request)

    except Exception as error:
        print("\nAPPLICATION ERROR:", error)


if __name__ == "__main__":
    asyncio.run(main())
