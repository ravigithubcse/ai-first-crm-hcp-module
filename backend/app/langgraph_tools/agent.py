# =============================================================================
# AI-First CRM HCP Module - LangGraph Agent
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.1.0
# Description : LangGraph agent for orchestrating HCP CRM tools
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
LangGraph Agent for HCP CRM Operations.

This agent orchestrates five specialized tools:
    1. Log Interaction   - Create and summarize interactions
    2. Edit Interaction  - Modify existing interactions
    3. View History      - Retrieve and analyze interaction history
    4. Generate Report   - Create structured call reports
    5. Schedule Follow-Up - Plan follow-up actions

Routing is LLM-driven: all five tools are bound to a Groq-hosted chat
model (llama-3.3-70b-versatile, chosen for its tool-calling reliability),
which reads the rep's message and the running conversation and decides
which tool to call and with what arguments -- a standard LangGraph
ReAct-style loop (agent node <-> tools node) built on the prebuilt
ToolNode/tools_condition helpers, rather than a fixed keyword pipeline.

Each tool is a thin @tool-wrapped adapter around the existing, already
LLM-powered implementation in this package (log_interaction.py etc.),
which continues to use gemma2-9b-it internally for entity extraction and
summarization exactly as before -- only the routing layer changed.
"""

import json
from typing import Any, Dict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.langgraph_tools.edit_interaction import edit_interaction as _edit_interaction
from app.langgraph_tools.generate_report import generate_call_report as _generate_report
from app.langgraph_tools.llm_config import get_llm_with_context
from app.langgraph_tools.log_interaction import log_interaction as _log_interaction
from app.langgraph_tools.schedule_followup import schedule_follow_up as _schedule_follow_up
from app.langgraph_tools.view_history import view_interaction_history as _view_history


@tool
def log_interaction_tool(description: str, interaction_type: str = "Meeting") -> str:
    """Log a new HCP interaction from a natural-language description, e.g.
    "Met Dr. Sharma, discussed OncoBoost Phase III efficacy, she seemed
    positive, left the brochure." Extracts the HCP name, topics, sentiment,
    materials/samples shared, and outcomes, then saves the record. Call
    this as soon as a rep describes a visit, call, or email worth saving
    -- don't wait to be asked explicitly.

    Args:
        description: The rep's free-text description of what happened.
        interaction_type: Meeting, Call, Email, Conference, or Virtual Meeting.
    """
    return json.dumps(_log_interaction(description=description, interaction_type=interaction_type))


@tool
def edit_interaction_tool(interaction_id: int, updates: str) -> str:
    """Edit an existing HCP interaction. Give the interaction_id and
    describe the change in plain language, e.g. "change the sentiment to
    positive" or "add that she asked for more samples".

    Args:
        interaction_id: The numeric ID of the interaction to change.
        updates: Plain-language description of what should change.
    """
    return json.dumps(_edit_interaction(interaction_id=interaction_id, updates=updates))


@tool
def view_history_tool(hcp_name: str = "", limit: int = 20) -> str:
    """Look up an HCP's past interaction history plus AI-generated
    insights, e.g. "show history for Dr. Sharma".

    Args:
        hcp_name: The healthcare professional's name to search for.
        limit: Maximum number of past interactions to return.
    """
    return json.dumps(_view_history(hcp_name=hcp_name, limit=limit))


@tool
def generate_report_tool(interaction_id: int, report_format: str = "structured") -> str:
    """Generate a structured call report for an already-logged interaction.

    Args:
        interaction_id: The numeric ID of the interaction to report on.
        report_format: "structured", "executive", or "detailed".
    """
    return json.dumps(_generate_report(interaction_id=interaction_id, report_format=report_format))


@tool
def schedule_followup_tool(interaction_id: int, description: str = "", due_date: str = "") -> str:
    """Schedule a follow-up action tied to a logged interaction, e.g.
    "schedule a follow-up meeting in 2 weeks" or "send the OncoBoost PDF
    next week".

    Args:
        interaction_id: The numeric ID of the interaction this follows up on.
        description: What the follow-up is, if the rep said.
        due_date: When it's due (e.g. "2026-07-25" or "in 2 weeks"), if said.
    """
    return json.dumps(
        _schedule_follow_up(interaction_id=interaction_id, description=description, due_date=due_date)
    )


ALL_TOOLS = [
    log_interaction_tool,
    edit_interaction_tool,
    view_history_tool,
    generate_report_tool,
    schedule_followup_tool,
]

SYSTEM_PROMPT = SystemMessage(
    content=(
        "You are the AI assistant embedded in a pharmaceutical field rep's "
        "CRM, on the 'Log HCP Interaction' screen. Reps describe meetings, "
        "calls, and emails with healthcare professionals (HCPs) in plain "
        "language; you turn that into accurate CRM records using your "
        "tools. Rules:\n"
        "- Call a tool as soon as you have enough information -- don't ask "
        "for details the rep already gave you.\n"
        "- Never invent an HCP name, outcome, or sentiment that wasn't "
        "stated or clearly implied.\n"
        "- After a tool runs, confirm in one short, friendly sentence what "
        "was saved, changed, or found.\n"
        "- If the message isn't about logging, editing, viewing, "
        "reporting on, or following up on an HCP interaction, answer "
        "briefly without calling a tool."
    )
)


def _call_model(state: MessagesState) -> Dict[str, Any]:
    llm = get_llm_with_context(temperature=0.2).bind_tools(ALL_TOOLS)
    response = llm.invoke([SYSTEM_PROMPT, *state["messages"]])
    return {"messages": [response]}


def build_agent_graph():
    """Build and compile the LangGraph agent state graph.

    Two nodes: `agent` (the LLM, with tools bound) and `tools` (executes
    whichever tool the LLM called). `tools_condition` routes to `tools`
    when the model's response contains a tool call, or to END when it
    doesn't; `tools` always loops back to `agent` so the model can turn
    the tool's result into a natural-language reply.
    """
    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", _call_model)
    workflow.add_node("tools", ToolNode(ALL_TOOLS))

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")

    return workflow.compile()


_compiled_graph = None


def _get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_agent_graph()
    return _compiled_graph


def run_agent(user_input: str) -> Dict[str, Any]:
    """
    Run the LangGraph agent on a single user message.

    Returns a dict shaped exactly like before (intent / message / result)
    so the existing /agent/chat route and frontend contract don't change:
      - intent: the name of the tool that ran, or "unknown" if none did.
      - message: the assistant's natural-language reply.
      - result: the structured payload the tool returned (drives the UI
        autofill), or {} if no tool ran.
    """
    graph = _get_graph()
    final_state = graph.invoke({"messages": [HumanMessage(content=user_input)]})
    messages = final_state["messages"]

    reply = next(
        (m.content for m in reversed(messages) if isinstance(m, AIMessage) and m.content),
        "Done.",
    )

    intent = "unknown"
    result: Dict[str, Any] = {}
    for m in messages:
        if isinstance(m, ToolMessage):
            try:
                result = json.loads(m.content)
            except (json.JSONDecodeError, TypeError):
                result = {"raw": m.content}
            intent = (m.name or intent).replace("_tool", "")

    return {"intent": intent, "message": reply, "result": result}
