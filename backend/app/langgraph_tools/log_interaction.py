# =============================================================================
# AI-First CRM HCP Module - Log Interaction Tool
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : LangGraph tool for logging HCP interactions with AI
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
Log Interaction Tool - AI-powered tool that captures interaction data
from natural language input, extracts entities, generates summaries,
and stores structured interaction records in the database.
"""

import json
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.hcp_service import HCPService
from app.services.interaction_service import InteractionService
from app.schemas.interaction import InteractionCreate
from app.langgraph_tools.llm_config import get_llm


def log_interaction(
    description: str,
    hcp_name: str = "",
    interaction_type: str = "Meeting",
    date_str: str = "",
) -> Dict[str, Any]:
    """
    Log an HCP interaction using AI-powered natural language processing.

    This tool:
    1. Parses natural language description using LLM
    2. Extracts entities (HCP name, topics, sentiment, etc.)
    3. Generates a structured summary
    4. Suggests follow-up actions
    5. Stores the interaction in the database

    Args:
        description: Natural language description of the interaction
        hcp_name: Optional HCP name (auto-detected if not provided)
        interaction_type: Type of interaction (Meeting, Call, Email, etc.)
        date_str: Optional date string (defaults to today)

    Returns:
        Dictionary containing the created interaction, AI summary,
        extracted entities, and suggested follow-ups
    """
    db = SessionLocal()
    try:
        # Use LLM to parse and extract information
        llm = get_llm(temperature=0.2)

        # Build the extraction prompt
        extraction_prompt = f"""You are an AI assistant for a pharmaceutical CRM system. 
Parse the following interaction description and extract structured information.

Description: {description}

Extract the following as JSON:
{{
    "hcp_name": "Name of the healthcare professional (if mentioned)",
    "topics_discussed": "Key topics/products discussed",
    "sentiment": "positive, neutral, or negative",
    "key_points": ["List of key discussion points"],
    "materials_shared": ["List of materials shared"],
    "samples_distributed": ["List of samples distributed"],
    "outcomes": "Key outcomes or agreements",
    "follow_up_suggestions": ["Suggested follow-up actions"],
    "attendees": ["List of attendees"],
    "summary": "A concise 2-3 sentence summary"
}}

Return ONLY valid JSON, no markdown formatting."""

        # Get LLM response
        response = llm.invoke(extraction_prompt)

        # Parse JSON response
        try:
            content = response.content.strip()
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            extracted = json.loads(content)
        except json.JSONDecodeError:
            # Fallback extraction
            extracted = {
                "hcp_name": hcp_name or "Unknown HCP",
                "topics_discussed": description,
                "sentiment": "neutral",
                "key_points": [],
                "materials_shared": [],
                "samples_distributed": [],
                "outcomes": "",
                "follow_up_suggestions": [
                    "Schedule follow-up meeting",
                    "Send additional materials",
                ],
                "attendees": [],
                "summary": description[:200],
            }

        # Find or create HCP
        hcp_name_found = extracted.get("hcp_name", hcp_name) or "Unknown HCP"

        # Search for existing HCP
        hcps = HCPService.search_by_name(db, hcp_name_found, limit=1)
        if hcps:
            hcp = hcps[0]
        else:
            # Create a new HCP with minimal info
            from app.schemas.hcp import HCPCreate

            hcp_data = HCPCreate(
                full_name=hcp_name_found,
                specialty="",
                notes=f"Auto-created from interaction log on {datetime.now().strftime('%Y-%m-%d')}",
            )
            hcp = HCPService.create(db, hcp_data)

        # Parse date
        try:
            interaction_date = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.now()
        except ValueError:
            interaction_date = datetime.now()

        # Create interaction
        interaction_data = InteractionCreate(
            hcp_id=hcp.id,
            interaction_type=interaction_type,
            date=interaction_date,
            attendees=extracted.get("attendees", []),
            topics_discussed=extracted.get("topics_discussed", ""),
            materials_shared=extracted.get("materials_shared", []),
            samples_distributed=extracted.get("samples_distributed", []),
            sentiment=extracted.get("sentiment", "neutral"),
            outcomes=extracted.get("outcomes", ""),
            summary=extracted.get("summary", ""),
            key_insights=extracted.get("key_points", []),
            follow_up_actions=extracted.get("follow_up_suggestions", []),
            source="chat",
        )

        interaction = InteractionService.create(db, interaction_data)

        return {
            "success": True,
            "interaction": interaction.to_dict(),
            "hcp": hcp.to_dict(),
            "ai_summary": extracted.get("summary", ""),
            "extracted_entities": {
                "hcp_name": hcp_name_found,
                "topics": extracted.get("topics_discussed", ""),
                "sentiment": extracted.get("sentiment", "neutral"),
                "materials": extracted.get("materials_shared", []),
                "samples": extracted.get("samples_distributed", []),
            },
            "follow_up_suggestions": extracted.get("follow_up_suggestions", []),
            "message": f"Interaction logged successfully for {hcp_name_found}.",
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to log interaction: {str(e)}",
        }
    finally:
        db.close()