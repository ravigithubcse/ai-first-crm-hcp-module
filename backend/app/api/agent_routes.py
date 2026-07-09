# =============================================================================
# AI-First CRM HCP Module - AI Agent API Routes
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : FastAPI routes for AI Agent chat and tool execution
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
FastAPI API routes for the LangGraph AI Agent.
Provides chat endpoint and direct tool access for the
conversational interface.
"""

from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.langgraph_tools.agent import run_agent
from app.langgraph_tools.log_interaction import log_interaction
from app.langgraph_tools.edit_interaction import edit_interaction
from app.langgraph_tools.view_history import view_interaction_history
from app.langgraph_tools.generate_report import generate_call_report
from app.langgraph_tools.schedule_followup import schedule_follow_up

router = APIRouter(prefix="/agent", tags=["AI Agent"])


class ChatRequest(BaseModel):
    """Request schema for AI agent chat."""
    message: str = Field(..., min_length=1, description="User message")


class ChatResponse(BaseModel):
    """Response schema for AI agent chat."""
    intent: str = Field(..., description="Detected intent")
    message: str = Field(..., description="Agent response message")
    result: Dict[str, Any] = Field(default_factory=dict, description="Tool execution result")


class ToolRequest(BaseModel):
    """Request schema for direct tool execution."""
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")


@router.post("/chat", response_model=ChatResponse)
def agent_chat(request: ChatRequest):
    """
    Chat with the AI Agent for natural language HCP CRM operations.

    The agent can:
    - Log interactions from natural language descriptions
    - Edit existing interactions
    - View interaction history
    - Generate call reports
    - Schedule follow-ups
    """
    try:
        result = run_agent(request.message)
        return {
            "intent": result.get("intent", "unknown"),
            "message": result.get("message", ""),
            "result": result.get("result", {}),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.post("/tools/execute")
def execute_tool_direct(request: ToolRequest):
    """
    Execute a specific LangGraph tool directly.

    Available tools:
    - log_interaction: Log a new interaction
    - edit_interaction: Edit an existing interaction
    - view_history: View interaction history
    - generate_report: Generate a call report
    - schedule_follow_up: Schedule a follow-up
    """
    try:
        tool_name = request.tool_name.lower()
        params = request.parameters

        if tool_name == "log_interaction":
            result = log_interaction(**params)
        elif tool_name == "edit_interaction":
            result = edit_interaction(**params)
        elif tool_name == "view_history":
            result = view_interaction_history(**params)
        elif tool_name == "generate_report":
            result = generate_call_report(**params)
        elif tool_name == "schedule_follow_up":
            result = schedule_follow_up(**params)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown tool: {tool_name}. Available tools: "
                       "log_interaction, edit_interaction, view_history, "
                       "generate_report, schedule_follow_up",
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution error: {str(e)}")


@router.get("/tools")
def list_tools():
    """List all available AI agent tools with descriptions."""
    return {
        "tools": [
            {
                "name": "log_interaction",
                "description": "Log a new HCP interaction with AI-powered entity extraction and summarization",
                "parameters": {
                    "description": "Natural language description of the interaction (required)",
                    "hcp_name": "HCP name (optional, auto-detected)",
                    "interaction_type": "Type: Meeting, Call, Email (default: Meeting)",
                    "date_str": "Date in YYYY-MM-DD format (default: today)",
                },
            },
            {
                "name": "edit_interaction",
                "description": "Edit an existing interaction using natural language or direct fields",
                "parameters": {
                    "interaction_id": "ID of interaction to edit (required)",
                    "updates": "Natural language description of changes (optional)",
                },
            },
            {
                "name": "view_history",
                "description": "View interaction history with AI-powered insights and analysis",
                "parameters": {
                    "hcp_id": "HCP ID to filter by (optional)",
                    "hcp_name": "HCP name to search for (optional)",
                    "start_date": "Filter from date YYYY-MM-DD (optional)",
                    "end_date": "Filter to date YYYY-MM-DD (optional)",
                    "limit": "Maximum results (default: 20)",
                },
            },
            {
                "name": "generate_report",
                "description": "Generate a structured call report from an interaction",
                "parameters": {
                    "interaction_id": "ID of interaction to generate report for (required)",
                    "report_format": "Format: structured, executive, detailed (default: structured)",
                },
            },
            {
                "name": "schedule_follow_up",
                "description": "Schedule a follow-up action with AI-powered suggestions",
                "parameters": {
                    "interaction_id": "Source interaction ID (required)",
                    "title": "Follow-up title (optional, auto-generated)",
                    "due_date": "Due date YYYY-MM-DD (optional, auto-suggested)",
                    "priority": "Priority: low, medium, high (default: medium)",
                },
            },
        ]
    }