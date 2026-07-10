# =============================================================================
# AI-First CRM HCP Module - View Interaction History Tool
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : LangGraph tool for retrieving HCP interaction history
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
View Interaction History Tool - AI-powered tool that retrieves,
filters, and analyzes historical interactions with HCPs.
Provides insights and summaries of past engagements.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from app.core.database import SessionLocal
from app.services.hcp_service import HCPService
from app.services.interaction_service import InteractionService
from app.langgraph_tools.llm_config import get_llm


def view_interaction_history(
    hcp_id: Optional[int] = None,
    hcp_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interaction_type: Optional[str] = None,
    limit: int = 20,
    include_ai_summary: bool = True,
) -> Dict[str, Any]:
    """
    Retrieve and analyze HCP interaction history with AI-powered insights.

    This tool:
    1. Finds HCP by ID or name
    2. Retrieves filtered interaction history
    3. Generates AI summary and insights
    4. Identifies patterns and trends
    5. Suggests engagement strategies

    Args:
        hcp_id: HCP ID to filter by
        hcp_name: HCP name to search for (if ID not provided)
        start_date: Filter from date (YYYY-MM-DD)
        end_date: Filter to date (YYYY-MM-DD)
        interaction_type: Filter by interaction type
        limit: Maximum number of interactions to retrieve
        include_ai_summary: Whether to generate AI insights

    Returns:
        Dictionary containing interaction history, statistics,
        AI-generated insights, and engagement suggestions
    """
    db = SessionLocal()
    try:
        # Resolve HCP
        hcp = None
        if hcp_id:
            hcp = HCPService.get_by_id(db, hcp_id)
        elif hcp_name:
            hcps = HCPService.search_by_name(db, hcp_name, limit=1)
            if hcps:
                hcp = hcps[0]
                hcp_id = hcp.id

        # Parse dates
        parsed_start = None
        parsed_end = None
        if start_date:
            try:
                parsed_start = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                pass
        if end_date:
            try:
                parsed_end = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                pass

        # Get interactions
        interactions, total = InteractionService.get_all(
            db=db,
            hcp_id=hcp_id,
            interaction_type=interaction_type,
            start_date=parsed_start,
            end_date=parsed_end,
            limit=limit,
        )

        if not interactions:
            return {
                "success": True,
                "interactions": [],
                "total": 0,
                "hcp": hcp.to_dict() if hcp else None,
                "message": "No interactions found for the given criteria.",
                "ai_summary": "",
                "insights": {},
            }

        # Convert to dict
        interaction_list = [i.to_dict() for i in interactions]

        # Calculate statistics
        sentiments = {}
        types = {}
        for interaction in interactions:
            sentiments[interaction.sentiment] = sentiments.get(interaction.sentiment, 0) + 1
            types[interaction.interaction_type] = types.get(interaction.interaction_type, 0) + 1

        # AI Summary
        ai_summary = ""
        insights = {}
        suggestions = []

        if include_ai_summary and interactions:
            llm = get_llm(temperature=0.3)

            # Build context for AI
            history_text = "\n\n".join([
                f"Interaction {i+1} ({interaction.interaction_type} on {interaction.date.strftime('%Y-%m-%d')}):\n"
                f"Topics: {interaction.topics_discussed or 'N/A'}\n"
                f"Sentiment: {interaction.sentiment}\n"
                f"Outcomes: {interaction.outcomes or 'N/A'}"
                for i, interaction in enumerate(interactions[:10])
            ])

            hcp_context = f"with {hcp.full_name}" if hcp else "across all HCPs"

            summary_prompt = f"""You are an AI assistant analyzing HCP interaction history.

Review the following interaction history {hcp_context}:

{history_text}

Provide:
1. A brief summary of the relationship and engagement pattern
2. Key insights about the HCP's interests and preferences
3. Recommended next steps for the field representative

Keep it concise and actionable."""

            try:
                response = llm.invoke(summary_prompt)
                ai_summary = response.content.strip()
            except Exception:
                ai_summary = "AI summary generation unavailable. Please review interactions manually."

            # Generate structured insights
            insights = {
                "total_interactions": total,
                "sentiment_distribution": sentiments,
                "interaction_types": types,
                "most_discussed_topics": _extract_common_topics(interactions),
                "engagement_trend": "Increasing" if total > 5 else "Steady",
            }

            suggestions = _generate_suggestions(interactions, sentiments)

        return {
            "success": True,
            "interactions": interaction_list,
            "total": total,
            "hcp": hcp.to_dict() if hcp else None,
            "statistics": {
                "by_sentiment": sentiments,
                "by_type": types,
            },
            "ai_summary": ai_summary,
            "insights": insights,
            "suggestions": suggestions,
            "message": f"Retrieved {total} interactions." + (
                f" for {hcp.full_name}" if hcp else ""
            ),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to retrieve interaction history: {str(e)}",
        }
    finally:
        db.close()


def _extract_common_topics(interactions) -> List[str]:
    """Extract commonly discussed topics from interactions."""
    topics = []
    for interaction in interactions:
        if interaction.topics_discussed:
            topics.extend(interaction.topics_discussed.split(", "))
    # Return unique topics (simplified)
    return list(set(t.strip() for t in topics if t.strip()))[:10]


def _generate_suggestions(interactions, sentiments) -> List[str]:
    """Generate engagement suggestions based on history."""
    suggestions = []

    if sentiments.get("negative", 0) > sentiments.get("positive", 0):
        suggestions.append("Consider addressing concerns raised in recent interactions.")

    if len(interactions) > 5:
        suggestions.append("Strong relationship - explore KOL partnership opportunities.")
    elif len(interactions) < 2:
        suggestions.append("Early-stage relationship - focus on building rapport.")

    if not any(i.follow_up_actions for i in interactions):
        suggestions.append("No follow-up actions recorded - consider scheduling next steps.")

    suggestions.append("Review materials shared to avoid duplication.")

    return suggestions