# =============================================================================
# AI-First CRM HCP Module - LangGraph Agent
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : LangGraph agent for orchestrating HCP CRM tools
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
LangGraph Agent for HCP CRM Operations.

This agent orchestrates five specialized tools:
    1. Log Interaction - Create and summarize interactions
    2. Edit Interaction - Modify existing interactions
    3. View Interaction History - Retrieve and analyze history
    4. Generate Call Report - Create structured reports
    5. Schedule Follow-Up - Plan follow-up actions

The agent uses a state graph to determine which tool to invoke
based on user intent and context.
"""

from typing import Dict, Any, TypedDict, Optional
from enum import Enum

from langgraph.graph import StateGraph, END

from app.langgraph_tools.log_interaction import log_interaction
from app.langgraph_tools.edit_interaction import edit_interaction
from app.langgraph_tools.view_history import view_interaction_history
from app.langgraph_tools.generate_report import generate_call_report
from app.langgraph_tools.schedule_followup import schedule_follow_up


class AgentIntent(str, Enum):
    """Possible agent intents based on user input."""
    LOG_INTERACTION = "log_interaction"
    EDIT_INTERACTION = "edit_interaction"
    VIEW_HISTORY = "view_history"
    GENERATE_REPORT = "generate_report"
    SCHEDULE_FOLLOWUP = "schedule_followup"
    UNKNOWN = "unknown"


class AgentState(TypedDict):
    """State structure for the LangGraph agent."""
    user_input: str
    intent: str
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    message: str


def classify_intent(state: AgentState) -> AgentState:
    """
    Classify user intent based on input text.
    Uses keyword matching to determine which tool to invoke.
    """
    user_input = state["user_input"].lower()

    # Intent classification logic
    if any(kw in user_input for kw in ["log", "record", "add interaction", "new visit", "met with", "called", "spoke with"]):
        intent = AgentIntent.LOG_INTERACTION
    elif any(kw in user_input for kw in ["edit", "update", "change", "modify interaction"]):
        intent = AgentIntent.EDIT_INTERACTION
    elif any(kw in user_input for kw in ["history", "past interactions", "previous visits", "all meetings", "show interactions"]):
        intent = AgentIntent.VIEW_HISTORY
    elif any(kw in user_input for kw in ["report", "summary", "generate report", "call report"]):
        intent = AgentIntent.GENERATE_REPORT
    elif any(kw in user_input for kw in ["schedule", "follow up", "follow-up", "reminder", "next meeting"]):
        intent = AgentIntent.SCHEDULE_FOLLOWUP
    else:
        intent = AgentIntent.UNKNOWN

    return {
        **state,
        "intent": intent.value,
    }


def extract_parameters(state: AgentState) -> AgentState:
    """
    Extract relevant parameters from user input based on intent.
    """
    intent = state["intent"]
    user_input = state["user_input"]
    parameters = {}

    if intent == AgentIntent.LOG_INTERACTION.value:
        # Extract interaction details
        parameters["description"] = user_input
        parameters["interaction_type"] = _detect_interaction_type(user_input)

    elif intent == AgentIntent.EDIT_INTERACTION.value:
        # Extract interaction ID and updates
        parameters["interaction_id"] = _extract_id(user_input)
        parameters["updates"] = user_input

    elif intent == AgentIntent.VIEW_HISTORY.value:
        # Extract HCP name or ID
        parameters["hcp_name"] = _extract_hcp_name(user_input)

    elif intent == AgentIntent.GENERATE_REPORT.value:
        # Extract interaction ID
        parameters["interaction_id"] = _extract_id(user_input)

    elif intent == AgentIntent.SCHEDULE_FOLLOWUP.value:
        # Extract interaction ID
        parameters["interaction_id"] = _extract_id(user_input)

    return {
        **state,
        "parameters": parameters,
    }


def execute_tool(state: AgentState) -> AgentState:
    """
    Execute the appropriate tool based on classified intent.
    """
    intent = state["intent"]
    params = state["parameters"]

    try:
        if intent == AgentIntent.LOG_INTERACTION.value:
            result = log_interaction(**params)

        elif intent == AgentIntent.EDIT_INTERACTION.value:
            result = edit_interaction(**params)

        elif intent == AgentIntent.VIEW_HISTORY.value:
            result = view_interaction_history(**params)

        elif intent == AgentIntent.GENERATE_REPORT.value:
            result = generate_call_report(**params)

        elif intent == AgentIntent.SCHEDULE_FOLLOWUP.value:
            result = schedule_follow_up(**params)

        else:
            result = {
                "success": False,
                "message": (
                    "I'm not sure how to help with that. "
                    "You can ask me to:\n"
                    "- Log an interaction (e.g., 'Met with Dr. Smith...')\n"
                    "- View interaction history (e.g., 'Show history for Dr. Smith')\n"
                    "- Generate a call report (e.g., 'Generate report for interaction 1')\n"
                    "- Schedule a follow-up (e.g., 'Schedule follow-up for interaction 1')\n"
                    "- Edit an interaction (e.g., 'Update interaction 1...')"
                ),
            }

        return {
            **state,
            "result": result,
            "message": result.get("message", "Operation completed."),
        }

    except Exception as e:
        return {
            **state,
            "result": {"success": False, "error": str(e)},
            "message": f"Error executing tool: {str(e)}",
        }


def build_agent_graph() -> StateGraph:
    """
    Build and compile the LangGraph agent state graph.

    Returns:
        Compiled StateGraph ready for invocation.
    """
    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("classify", classify_intent)
    workflow.add_node("extract", extract_parameters)
    workflow.add_node("execute", execute_tool)

    # Add edges
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "extract")
    workflow.add_edge("extract", "execute")
    workflow.add_edge("execute", END)

    return workflow.compile()


def run_agent(user_input: str) -> Dict[str, Any]:
    """
    Run the LangGraph agent with user input.

    Args:
        user_input: Natural language user query or command.

    Returns:
        Agent result dictionary.
    """
    graph = build_agent_graph()

    initial_state: AgentState = {
        "user_input": user_input,
        "intent": "",
        "parameters": {},
        "result": None,
        "message": "",
    }

    result = graph.invoke(initial_state)
    return {
        "intent": result["intent"],
        "message": result["message"],
        "result": result["result"],
    }


# Helper functions

def _detect_interaction_type(text: str) -> str:
    """Detect interaction type from text."""
    text_lower = text.lower()
    if any(kw in text_lower for kw in ["call", "phone", "rang"]):
        return "Call"
    elif any(kw in text_lower for kw in ["email", "wrote", "messaged"]):
        return "Email"
    elif any(kw in text_lower for kw in ["conference", "presentation"]):
        return "Conference"
    elif any(kw in text_lower for kw in ["virtual", "zoom", "teams", "video"]):
        return "Virtual Meeting"
    else:
        return "Meeting"


def _extract_id(text: str) -> int:
    """Extract numeric ID from text."""
    import re
    numbers = re.findall(r'\d+', text)
    if numbers:
        return int(numbers[0])
    return 1  # Default


def _extract_hcp_name(text: str) -> str:
    """Extract HCP name from text."""
    import re
    # Look for patterns like "Dr. Name" or "for Name"
    patterns = [
        r'(?:for|with|of)\s+(?:Dr\.?\s+)?([A-Z][a-zA-Z\s]+?)(?:\s|$|\.|:)',
        r'(?:Dr\.?\s+)([A-Z][a-zA-Z\s]+?)(?:\s|$|\.|:)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""