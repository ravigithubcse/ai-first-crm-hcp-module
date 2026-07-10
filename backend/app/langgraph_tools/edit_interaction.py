# =============================================================================
# AI-First CRM HCP Module - Edit Interaction Tool
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : LangGraph tool for editing HCP interactions
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
Edit Interaction Tool - AI-powered tool that allows modification
of logged interaction data through natural language commands or
structured field updates.
"""

from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.interaction_service import InteractionService
from app.schemas.interaction import InteractionUpdate
from app.langgraph_tools.llm_config import get_llm


def edit_interaction(
    interaction_id: int,
    updates: str = "",
    **field_updates: Any,
) -> Dict[str, Any]:
    """
    Edit an existing HCP interaction using AI-powered parsing or direct fields.

    This tool:
    1. Retrieves the existing interaction
    2. Parses natural language update instructions using LLM
    3. Applies structured field updates
    4. Validates the updated data
    5. Saves changes to the database

    Args:
        interaction_id: ID of the interaction to edit
        updates: Natural language description of changes to make
        **field_updates: Direct field updates (e.g., sentiment="positive")

    Returns:
        Dictionary containing the updated interaction and change summary

    Examples:
        edit_interaction(1, "Change sentiment to positive and add follow-up")
        edit_interaction(1, sentiment="positive", outcomes="New agreement reached")
    """
    db = SessionLocal()
    try:
        # Get existing interaction
        interaction = InteractionService.get_by_id(db, interaction_id)
        if not interaction:
            return {
                "success": False,
                "message": f"Interaction with ID {interaction_id} not found.",
            }

        # Build update data
        update_data = {}

        # Parse natural language updates
        if updates:
            llm = get_llm(temperature=0.2)

            parse_prompt = f"""You are an AI assistant for a pharmaceutical CRM system.
Given the current interaction data and the requested changes, extract field updates.

Current interaction:
- Type: {interaction.interaction_type}
- Topics: {interaction.topics_discussed or 'N/A'}
- Sentiment: {interaction.sentiment}
- Outcomes: {interaction.outcomes or 'N/A'}
- Next Steps: {interaction.next_steps or 'N/A'}

Requested changes: {updates}

Extract updates as JSON with these possible fields:
{{
    "interaction_type": "new type if changed",
    "topics_discussed": "updated topics",
    "sentiment": "updated sentiment",
    "outcomes": "updated outcomes",
    "next_steps": "updated next steps",
    "materials_shared": ["updated materials"],
    "samples_distributed": ["updated samples"],
    "attendees": ["updated attendees"]
}}

Include ONLY fields that need to change. Return valid JSON only."""

            response = llm.invoke(parse_prompt)
            content = response.content.strip()

            # Clean markdown formatting
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            try:
                import json
                parsed_updates = json.loads(content)
                update_data.update({k: v for k, v in parsed_updates.items() if v})
            except json.JSONDecodeError:
                # If parsing fails, try to extract from direct fields
                pass

        # Apply direct field updates
        for key, value in field_updates.items():
            if value is not None:
                update_data[key] = value

        # Validate and clean update data
        valid_fields = {
            "interaction_type", "topics_discussed", "sentiment",
            "outcomes", "next_steps", "materials_shared",
            "samples_distributed", "attendees", "hcp_id",
        }
        update_data = {k: v for k, v in update_data.items() if k in valid_fields}

        if not update_data:
            return {
                "success": False,
                "message": "No valid fields to update. Please provide changes.",
                "interaction": interaction.to_dict(),
            }

        # Create update schema
        update_schema = InteractionUpdate(**update_data)

        # Apply updates
        updated = InteractionService.update(db, interaction_id, update_schema)

        if not updated:
            return {
                "success": False,
                "message": "Failed to update interaction.",
            }

        # Generate change summary
        changes = ", ".join([f"{k}: {v}" for k, v in update_data.items()])

        return {
            "success": True,
            "interaction": updated.to_dict(),
            "changes_made": changes,
            "message": f"Interaction {interaction_id} updated successfully. Changes: {changes}",
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to edit interaction: {str(e)}",
        }
    finally:
        db.close()