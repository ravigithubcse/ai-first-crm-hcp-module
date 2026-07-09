# =============================================================================
# AI-First CRM HCP Module - Schedule Follow-Up Tool
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : LangGraph tool for scheduling follow-up actions
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
Schedule Follow-Up Tool - AI-powered tool that creates follow-up
actions based on interaction content and suggests optimal timing,
priority, and action types.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from app.core.database import SessionLocal
from app.services.follow_up_service import FollowUpService
from app.services.interaction_service import InteractionService
from app.services.hcp_service import HCPService
from app.schemas.follow_up import FollowUpCreate
from app.langgraph_tools.llm_config import get_llm


def schedule_follow_up(
    interaction_id: int,
    title: str = "",
    description: str = "",
    due_date: str = "",
    priority: str = "medium",
    assigned_to: str = "",
    action_type: str = "",
    auto_generate: bool = True,
) -> Dict[str, Any]:
    """
    Schedule a follow-up action based on an HCP interaction.

    This tool:
    1. Retrieves the source interaction
    2. Uses AI to suggest optimal follow-up details
    3. Creates the follow-up record in the database
    4. Provides calendar-ready event data
    5. Suggests additional follow-up actions

    Args:
        interaction_id: ID of the source interaction
        title: Follow-up title (auto-generated if not provided)
        description: Detailed description
        due_date: Due date string (YYYY-MM-DD, auto if not provided)
        priority: Priority level (low, medium, high)
        assigned_to: Person responsible
        action_type: Type of follow-up action
        auto_generate: Whether to use AI for auto-generation

    Returns:
        Dictionary containing the created follow-up, calendar event data,
        suggestions, and confirmation message
    """
    db = SessionLocal()
    try:
        # Get interaction
        interaction = InteractionService.get_by_id(db, interaction_id)
        if not interaction:
            return {
                "success": False,
                "message": f"Interaction with ID {interaction_id} not found.",
            }

        # Get HCP info
        hcp = HCPService.get_by_id(db, interaction.hcp_id)
        hcp_name = hcp.full_name if hcp else "Unknown HCP"

        # AI Auto-generation
        if auto_generate and not title:
            llm = get_llm(temperature=0.3)

            ai_prompt = f"""You are an AI assistant scheduling follow-ups for pharmaceutical sales.

Based on this interaction:
- HCP: {hcp_name}
- Type: {interaction.interaction_type}
- Topics: {interaction.topics_discussed or 'N/A'}
- Outcomes: {interaction.outcomes or 'N/A'}
- Next Steps: {interaction.next_steps or 'N/A'}
- Sentiment: {interaction.sentiment}

Generate a follow-up plan as JSON:
{{
    "title": "Concise follow-up title (max 100 chars)",
    "description": "Detailed follow-up description",
    "suggested_due_days": "Number of days from now (integer)",
    "priority": "low, medium, or high",
    "action_type": "email, meeting, call, send_material, or other",
    "additional_suggestions": ["Other follow-up ideas"]
}}

Return valid JSON only."""

            try:
                response = llm.invoke(ai_prompt)
                content = response.content.strip()

                # Clean markdown
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

                import json
                ai_plan = json.loads(content)

                title = title or ai_plan.get("title", f"Follow-up with {hcp_name}")
                description = description or ai_plan.get(
                    "description", f"Follow-up on {interaction.interaction_type} with {hcp_name}"
                )

                if not due_date and ai_plan.get("suggested_due_days"):
                    try:
                        days = int(ai_plan["suggested_due_days"])
                        due_dt = datetime.now() + timedelta(days=days)
                        due_date = due_dt.strftime("%Y-%m-%d")
                    except (ValueError, TypeError):
                        due_dt = datetime.now() + timedelta(days=7)
                        due_date = due_dt.strftime("%Y-%m-%d")

                priority = priority or ai_plan.get("priority", "medium")
                action_type = action_type or ai_plan.get("action_type", "meeting")
                additional_suggestions = ai_plan.get("additional_suggestions", [])

            except Exception:
                # Fallback defaults
                title = title or f"Follow-up with {hcp_name}"
                description = description or f"Follow up on {interaction.interaction_type}"
                if not due_date:
                    due_dt = datetime.now() + timedelta(days=7)
                    due_date = due_dt.strftime("%Y-%m-%d")
                action_type = action_type or "meeting"
                additional_suggestions = []

        # Set defaults if still empty
        if not title:
            title = f"Follow-up with {hcp_name}"
        if not description:
            description = f"Follow up on {interaction.interaction_type} with {hcp_name}"
        if not due_date:
            due_dt = datetime.now() + timedelta(days=7)
            due_date = due_dt.strftime("%Y-%m-%d")
        if not action_type:
            action_type = "meeting"

        # Parse due date
        try:
            due_datetime = datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            due_datetime = datetime.now() + timedelta(days=7)

        # Create follow-up
        follow_up_data = FollowUpCreate(
            interaction_id=interaction_id,
            title=title,
            description=description,
            due_date=due_datetime,
            priority=priority,
            assigned_to=assigned_to or "Field Representative",
            action_type=action_type,
            ai_suggested=auto_generate,
        )

        follow_up = FollowUpService.create(db, follow_up_data)

        # Generate calendar event data
        calendar_event = {
            "title": title,
            "description": description,
            "start": due_datetime.isoformat(),
            "duration_minutes": 60,
            "location": "TBD",
            "attendees": [hcp_name] if hcp else [],
        }

        return {
            "success": True,
            "follow_up": follow_up.to_dict(),
            "calendar_event": calendar_event,
            "additional_suggestions": additional_suggestions if auto_generate else [],
            "message": (
                f"Follow-up '{title}' scheduled for {due_date} "
                f"with {hcp_name}."
            ),
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to schedule follow-up: {str(e)}",
        }
    finally:
        db.close()