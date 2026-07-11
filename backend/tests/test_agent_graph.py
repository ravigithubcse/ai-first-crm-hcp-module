# =============================================================================
# AI-First CRM HCP Module - Agent Graph Tests
# =============================================================================
# Author  : Ravi Kumar
# Version : 1.0.0
# Structural checks for the LangGraph agent that don't require a live Groq
# call (api.groq.com access isn't guaranteed in every environment this runs
# in -- CI, a reviewer's sandbox, etc.). These confirm the graph wiring and
# tool registration are correct; the actual reasoning is exercised manually
# via the chat panel once GROQ_API_KEY is set to a real key.
# =============================================================================
from app.langgraph_tools.agent import ALL_TOOLS, build_agent_graph


def test_graph_has_agent_and_tools_nodes():
    graph = build_agent_graph()
    nodes = set(graph.get_graph().nodes.keys())
    assert {"agent", "tools"}.issubset(nodes)


def test_all_five_tools_are_registered_with_valid_schemas():
    names = {t.name for t in ALL_TOOLS}
    assert names == {
        "log_interaction_tool", "edit_interaction_tool", "view_history_tool",
        "generate_report_tool", "schedule_followup_tool",
    }
    for t in ALL_TOOLS:
        assert t.description, f"{t.name} is missing a docstring the LLM needs to pick it"


def test_log_interaction_tool_wraps_the_real_implementation():
    # The @tool wrapper should call straight through to the existing,
    # already-Groq-powered log_interaction() without altering its behavior --
    # this just proves the adapter forwards arguments correctly, independent
    # of whether a real LLM call succeeds.
    import json
    from unittest.mock import patch

    with patch(
        "app.langgraph_tools.agent._log_interaction",
        return_value={"success": True, "message": "ok"},
    ) as mocked:
        result = json.loads(ALL_TOOLS[0].invoke({"description": "Met Dr. Smith, discussed Product X"}))
        mocked.assert_called_once_with(description="Met Dr. Smith, discussed Product X", interaction_type="Meeting")
        assert result == {"success": True, "message": "ok"}
