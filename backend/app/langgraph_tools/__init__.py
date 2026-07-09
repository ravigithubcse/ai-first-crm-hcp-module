# =============================================================================
# AI-First CRM HCP Module - LangGraph Tools Package
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : LangGraph AI Agent tools for HCP CRM operations
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
LangGraph tools package providing AI-powered capabilities
for managing HCP interactions through an intelligent agent.

Tools:
    - Log Interaction: Create and summarize interaction records
    - Edit Interaction: Modify existing interaction data
    - View Interaction History: Retrieve and analyze past interactions
    - Generate Call Report: Create structured reports from interactions
    - Schedule Follow-up: Plan and create follow-up actions
"""

from app.langgraph_tools.log_interaction import log_interaction
from app.langgraph_tools.edit_interaction import edit_interaction
from app.langgraph_tools.view_history import view_interaction_history
from app.langgraph_tools.generate_report import generate_call_report
from app.langgraph_tools.schedule_followup import schedule_follow_up

__all__ = [
    "log_interaction",
    "edit_interaction",
    "view_interaction_history",
    "generate_call_report",
    "schedule_follow_up",
]