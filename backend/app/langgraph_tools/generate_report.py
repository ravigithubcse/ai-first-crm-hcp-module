# =============================================================================
# AI-First CRM HCP Module - Generate Call Report Tool
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : LangGraph tool for generating structured call reports
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
Generate Call Report Tool - AI-powered tool that creates comprehensive,
structured call reports from interaction data for field representatives
to share with management and marketing teams.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from app.core.database import SessionLocal
from app.services.interaction_service import InteractionService
from app.services.hcp_service import HCPService
from app.langgraph_tools.llm_config import get_llm, get_llm_with_context


def generate_call_report(
    interaction_id: int,
    report_format: str = "structured",
    include_recommendations: bool = True,
) -> Dict[str, Any]:
    """
    Generate a structured call report from an HCP interaction.

    This tool:
    1. Retrieves the interaction with HCP details
    2. Analyzes the interaction content using LLM
    3. Generates a professional call report
    4. Extracts key highlights and action items
    5. Provides strategic recommendations

    Args:
        interaction_id: ID of the interaction to generate report for
        report_format: Format type (structured, executive, detailed)
        include_recommendations: Whether to include strategic recommendations

    Returns:
        Dictionary containing the formatted report, highlights,
        recommendations, and report metadata
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

        # Get HCP details
        hcp = HCPService.get_by_id(db, interaction.hcp_id)
        hcp_name = hcp.full_name if hcp else "Unknown HCP"
        hcp_specialty = hcp.specialty if hcp else ""
        hcp_institution = hcp.institution if hcp else ""

        # Build interaction context
        interaction_data = interaction.to_dict()

        # Generate report using LLM
        try:
            if report_format == "detailed":
                llm = get_llm_with_context(temperature=0.3)
            else:
                llm = get_llm(temperature=0.3)

            report_prompt = _build_report_prompt(
                interaction=interaction,
                hcp_name=hcp_name,
                hcp_specialty=hcp_specialty,
                hcp_institution=hcp_institution,
                report_format=report_format,
                include_recommendations=include_recommendations,
            )

            response = llm.invoke(report_prompt)
            report_content = response.content.strip()

            # Extract key highlights
            highlights = _extract_highlights(interaction)

            # Generate recommendations
            recommendations = []
            if include_recommendations:
                recommendations = _generate_recommendations(
                    interaction, hcp_name, llm
                )

            return {
                "success": True,
                "report": report_content,
                "highlights": highlights,
                "recommendations": recommendations,
                "metadata": {
                    "interaction_id": interaction_id,
                    "hcp_name": hcp_name,
                    "hcp_specialty": hcp_specialty,
                    "hcp_institution": hcp_institution,
                    "interaction_date": interaction.date.isoformat() if interaction.date else None,
                    "interaction_type": interaction.interaction_type,
                    "generated_at": datetime.now().isoformat(),
                    "report_format": report_format,
                },
                "message": f"Call report generated for interaction with {hcp_name}.",
            }

        except Exception as e:
            # Fallback to template-based report
            report = _generate_template_report(
                interaction, hcp_name, hcp_specialty, hcp_institution
            )
            return {
                "success": True,
                "report": report,
                "highlights": _extract_highlights(interaction),
                "recommendations": [
                    "Schedule follow-up within 2 weeks",
                    "Share relevant clinical data",
                    "Update HCP profile with new insights",
                ],
                "metadata": {
                    "interaction_id": interaction_id,
                    "hcp_name": hcp_name,
                    "generated_at": datetime.now().isoformat(),
                    "report_format": report_format,
                },
                "message": f"Template report generated for {hcp_name}.",
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate report: {str(e)}",
        }
    finally:
        db.close()


def _build_report_prompt(
    interaction,
    hcp_name: str,
    hcp_specialty: str,
    hcp_institution: str,
    report_format: str,
    include_recommendations: bool,
) -> str:
    """Build the prompt for report generation."""

    format_instructions = {
        "structured": """Generate a structured call report with these sections:
1. EXECUTIVE SUMMARY - Brief overview
2. HCP PROFILE - Name, specialty, institution
3. VISIT DETAILS - Date, type, attendees
4. DISCUSSION SUMMARY - Key topics discussed
5. KEY OUTCOMES - Agreements and decisions
6. SENTIMENT ANALYSIS - HCP attitude and receptiveness
7. NEXT STEPS - Agreed follow-up actions
8. MATERIALS SHARED - Documents/samples provided""",
        "executive": """Generate a concise executive summary including:
- Key takeaways (3-5 bullet points)
- HCP sentiment and engagement level
- Critical action items
- Strategic implications""",
        "detailed": """Generate a comprehensive call report including:
1. VISIT OVERVIEW - Complete context
2. DETAILED DISCUSSION - All topics covered
3. HCP RESPONSES - Specific reactions and feedback
4. OBJECTIONS/CONCERNS - Any hesitations raised
5. COMPETITIVE INTELLIGENCE - Mentions of competitors
6. OPPORTUNITIES - Potential next steps
7. RISK FACTORS - Anything to monitor
8. STRATEGIC RECOMMENDATIONS - Long-term suggestions""",
    }

    sections = format_instructions.get(report_format, format_instructions["structured"])

    prompt = f"""You are an expert pharmaceutical sales analyst generating a professional call report.

{sections}

Interaction Data:
- HCP: {hcp_name} ({hcp_specialty}) at {hcp_institution}
- Date: {interaction.date.strftime('%Y-%m-%d') if interaction.date else 'N/A'}
- Type: {interaction.interaction_type}
- Attendees: {', '.join(interaction.attendees) if interaction.attendees else 'Not recorded'}
- Topics Discussed: {interaction.topics_discussed or 'N/A'}
- Outcomes: {interaction.outcomes or 'N/A'}
- Next Steps: {interaction.next_steps or 'N/A'}
- Sentiment: {interaction.sentiment}
- Materials Shared: {', '.join(interaction.materials_shared) if interaction.materials_shared else 'None'}
- Samples Distributed: {', '.join(interaction.samples_distributed) if interaction.samples_distributed else 'None'}
- AI Summary: {interaction.summary or 'N/A'}
- Key Insights: {', '.join(interaction.key_insights) if interaction.key_insights else 'None'}

Generate a professional, well-formatted call report."""

    if include_recommendations:
        prompt += "\n\nInclude strategic recommendations for future engagement."

    return prompt


def _extract_highlights(interaction) -> list:
    """Extract key highlights from the interaction."""
    highlights = []

    if interaction.sentiment == "positive":
        highlights.append("HCP expressed positive sentiment during the interaction.")
    elif interaction.sentiment == "negative":
        highlights.append("HCP expressed concerns that need to be addressed.")

    if interaction.outcomes:
        highlights.append(f"Key outcome: {interaction.outcomes[:100]}")

    if interaction.materials_shared:
        highlights.append(f"Materials shared: {', '.join(interaction.materials_shared[:3])}")

    if interaction.samples_distributed:
        highlights.append(f"Samples distributed: {', '.join(interaction.samples_distributed[:3])}")

    if not highlights:
        highlights.append("Interaction logged successfully.")

    return highlights


def _generate_recommendations(interaction, hcp_name: str, llm) -> list:
    """Generate strategic recommendations using LLM."""
    try:
        rec_prompt = f"""Based on this interaction with {hcp_name}:
- Topics: {interaction.topics_discussed or 'N/A'}
- Sentiment: {interaction.sentiment}
- Outcomes: {interaction.outcomes or 'N/A'}

Provide 3-5 strategic recommendations for future engagement.
Return as a numbered list."""

        response = llm.invoke(rec_prompt)
        recommendations = [
            line.strip()
            for line in response.content.strip().split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]
        return recommendations[:5]
    except Exception:
        return [
            "Schedule follow-up meeting within 2 weeks",
            "Share relevant clinical publications",
            "Monitor HCP feedback on discussed topics",
            "Update CRM with new insights",
        ]


def _generate_template_report(
    interaction, hcp_name: str, hcp_specialty: str, hcp_institution: str
) -> str:
    """Generate a template-based report as fallback."""
    return f"""# CALL REPORT

## HCP Information
- **Name:** {hcp_name}
- **Specialty:** {hcp_specialty or 'N/A'}
- **Institution:** {hcp_institution or 'N/A'}

## Visit Details
- **Date:** {interaction.date.strftime('%Y-%m-%d') if interaction.date else 'N/A'}
- **Type:** {interaction.interaction_type}
- **Attendees:** {', '.join(interaction.attendees) if interaction.attendees else 'N/A'}

## Discussion Summary
{interaction.topics_discussed or 'No detailed discussion recorded.'}

## Key Outcomes
{interaction.outcomes or 'No outcomes recorded.'}

## Sentiment
{interaction.sentiment.title()}

## Materials Shared
{', '.join(interaction.materials_shared) if interaction.materials_shared else 'None'}

## Next Steps
{interaction.next_steps or 'No next steps recorded.'}

---
*Report generated by AI-First CRM HCP Module*
*Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"""