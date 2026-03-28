"""MCP server exposing HR Assistant tools over stdio transport."""

import asyncio
import json
import os
import sys
from datetime import date, datetime
from typing import Any, Optional

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Base URL for the HR Assistant REST API
HR_API_BASE = os.environ.get("HR_API_BASE", "http://localhost:5000/api")

app = Server("hr-assistant")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

async def _api_get(path: str, params: Optional[dict] = None) -> dict:
    """Perform an async GET request against the HR API.

    Args:
        path: URL path relative to HR_API_BASE.
        params: Optional query parameters.

    Returns:
        Parsed JSON response body.

    Raises:
        httpx.HTTPStatusError: On non-2xx responses.
    """
    async with httpx.AsyncClient(base_url=HR_API_BASE, timeout=30) as client:
        response = await client.get(path, params=params)
        response.raise_for_status()
        return response.json()


async def _api_post(path: str, payload: dict) -> dict:
    """Perform an async POST request against the HR API.

    Args:
        path: URL path relative to HR_API_BASE.
        payload: JSON body to send.

    Returns:
        Parsed JSON response body.

    Raises:
        httpx.HTTPStatusError: On non-2xx responses.
    """
    async with httpx.AsyncClient(base_url=HR_API_BASE, timeout=30) as client:
        response = await client.post(path, json=payload)
        response.raise_for_status()
        return response.json()


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Advertise available HR tools to the MCP client."""
    return [
        Tool(
            name="get_employee_info",
            description=(
                "Retrieve detailed information about an employee. "
                "Provide either employee_id (integer) or email (string)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "integer",
                        "description": "The employee's numeric ID.",
                    },
                    "email": {
                        "type": "string",
                        "description": "The employee's work email address.",
                    },
                },
                "anyOf": [{"required": ["employee_id"]}, {"required": ["email"]}],
            },
        ),
        Tool(
            name="answer_hr_question",
            description=(
                "Answer a natural-language question about HR policies, leave entitlements, "
                "expense procedures, benefits, or onboarding. Uses the company HR policy documents."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The HR policy question to answer.",
                    },
                    "employee_id": {
                        "type": "integer",
                        "description": "Optional employee ID for personalised context.",
                    },
                },
                "required": ["question"],
            },
        ),
        Tool(
            name="submit_leave_request",
            description="Submit a leave request on behalf of an employee.",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "integer",
                        "description": "The employee's numeric ID.",
                    },
                    "leave_type": {
                        "type": "string",
                        "enum": ["annual", "sick", "maternity", "paternity", "unpaid", "compassionate", "other"],
                        "description": "Type of leave.",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format.",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Optional reason for the leave.",
                    },
                },
                "required": ["employee_id", "leave_type", "start_date", "end_date"],
            },
        ),
        Tool(
            name="submit_expense_claim",
            description="Submit an expense reimbursement claim on behalf of an employee.",
            inputSchema={
                "type": "object",
                "properties": {
                    "employee_id": {
                        "type": "integer",
                        "description": "The employee's numeric ID.",
                    },
                    "amount": {
                        "type": "number",
                        "description": "Claimed amount (must be positive).",
                    },
                    "currency": {
                        "type": "string",
                        "description": "ISO 4217 currency code, e.g. USD, GBP.",
                        "default": "USD",
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the expense.",
                    },
                    "category": {
                        "type": "string",
                        "description": "Expense category (e.g. Travel, Meals, Equipment).",
                    },
                    "receipt_url": {
                        "type": "string",
                        "description": "Optional URL to the receipt.",
                    },
                },
                "required": ["employee_id", "amount", "description", "category"],
            },
        ),
        Tool(
            name="list_employees",
            description="List employees, optionally filtered by department.",
            inputSchema={
                "type": "object",
                "properties": {
                    "department_id": {
                        "type": "integer",
                        "description": "Filter employees to this department ID.",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (default 1).",
                        "default": 1,
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Results per page (default 20, max 100).",
                        "default": 20,
                    },
                },
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Tool call handlers
# ---------------------------------------------------------------------------

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Dispatch tool calls to the appropriate handler.

    Args:
        name: Tool name as advertised in list_tools.
        arguments: Input arguments provided by the MCP client.

    Returns:
        List containing a single TextContent with the result.
    """
    try:
        if name == "get_employee_info":
            result = await _handle_get_employee_info(arguments)
        elif name == "answer_hr_question":
            result = await _handle_answer_hr_question(arguments)
        elif name == "submit_leave_request":
            result = await _handle_submit_leave_request(arguments)
        elif name == "submit_expense_claim":
            result = await _handle_submit_expense_claim(arguments)
        elif name == "list_employees":
            result = await _handle_list_employees(arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}
    except httpx.HTTPStatusError as exc:
        result = {
            "error": f"API request failed with status {exc.response.status_code}",
            "detail": exc.response.text,
        }
    except Exception as exc:
        result = {"error": str(exc)}

    return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]


async def _handle_get_employee_info(args: dict) -> dict:
    employee_id = args.get("employee_id")
    email = args.get("email")

    if employee_id:
        return await _api_get(f"/employees/{employee_id}")

    # Search by email via the list endpoint
    data = await _api_get("/employees", params={"per_page": 200})
    for emp in data.get("items", []):
        if emp.get("email", "").lower() == email.lower():
            return emp

    return {"error": f"No employee found with email: {email}"}


async def _handle_answer_hr_question(args: dict) -> dict:
    question = args["question"]
    employee_id = args.get("employee_id")
    payload = {"message": question}
    if employee_id:
        payload["employee_id"] = employee_id
    return await _api_post("/chat", payload)


async def _handle_submit_leave_request(args: dict) -> dict:
    employee_id = args["employee_id"]
    payload = {
        "employee_id": employee_id,
        "leave_type": args["leave_type"],
        "start_date": args["start_date"],
        "end_date": args["end_date"],
        "reason": args.get("reason", ""),
    }
    return await _api_post(f"/employees/{employee_id}/leave-requests", payload)


async def _handle_submit_expense_claim(args: dict) -> dict:
    employee_id = args["employee_id"]
    payload = {
        "employee_id": employee_id,
        "amount": str(args["amount"]),
        "currency": args.get("currency", "USD"),
        "description": args["description"],
        "category": args["category"],
    }
    if "receipt_url" in args:
        payload["receipt_url"] = args["receipt_url"]
    return await _api_post(f"/employees/{employee_id}/expense-claims", payload)


async def _handle_list_employees(args: dict) -> dict:
    params: dict[str, Any] = {
        "page": args.get("page", 1),
        "per_page": min(args.get("per_page", 20), 100),
    }
    if "department_id" in args:
        params["department_id"] = args["department_id"]
    return await _api_get("/employees", params=params)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    """Start the MCP server using stdio transport."""
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
