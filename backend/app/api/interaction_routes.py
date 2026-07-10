# =============================================================================
# AI-First CRM HCP Module - Interaction API Routes
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : FastAPI routes for Interaction CRUD operations
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
FastAPI API routes for HCP Interaction management.
Provides CRUD endpoints and AI-powered chat logging.
"""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.interaction import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
    InteractionListResponse,
    ChatInteractionRequest,
    ChatInteractionResponse,
    CallReportRequest,
    CallReportResponse,
)
from app.services.interaction_service import InteractionService
from app.services.hcp_service import HCPService
from app.langgraph_tools.log_interaction import log_interaction
from app.langgraph_tools.generate_report import generate_call_report as gen_report_tool

router = APIRouter(prefix="/interactions", tags=["Interactions"])


@router.post("", response_model=InteractionResponse, status_code=201)
def create_interaction(data: InteractionCreate, db: Session = Depends(get_db)):
    """Create a new interaction record."""
    # Verify HCP exists
    hcp = HCPService.get_by_id(db, data.hcp_id)
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    interaction = InteractionService.create(db, data)
    return interaction.to_dict()


@router.get("", response_model=InteractionListResponse)
def list_interactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    hcp_id: Optional[int] = Query(None),
    interaction_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List interactions with pagination and filtering."""
    skip = (page - 1) * page_size

    parsed_start = None
    parsed_end = None
    if start_date:
        parsed_start = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        parsed_end = datetime.strptime(end_date, "%Y-%m-%d")

    items, total = InteractionService.get_all(
        db,
        skip=skip,
        limit=page_size,
        hcp_id=hcp_id,
        interaction_type=interaction_type,
        start_date=parsed_start,
        end_date=parsed_end,
    )
    return {
        "items": [i.to_dict() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """Get a specific interaction by ID."""
    interaction = InteractionService.get_by_id(db, interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction.to_dict()


@router.put("/{interaction_id}", response_model=InteractionResponse)
def update_interaction(
    interaction_id: int, data: InteractionUpdate, db: Session = Depends(get_db)
):
    """Update an interaction."""
    interaction = InteractionService.update(db, interaction_id, data)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction.to_dict()


@router.delete("/{interaction_id}", status_code=204)
def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """Delete an interaction."""
    success = InteractionService.delete(db, interaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return None


@router.get("/hcp/{hcp_id}/history")
def get_hcp_interactions(
    hcp_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Get all interactions for a specific HCP."""
    items = InteractionService.get_by_hcp(db, hcp_id, limit)
    return {
        "items": [i.to_dict() for i in items],
        "total": len(items),
    }


@router.get("/recent/all")
def get_recent_interactions(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get recent interactions across all HCPs."""
    items = InteractionService.get_recent(db, limit)
    return {
        "items": [i.to_dict() for i in items],
        "total": len(items),
    }


@router.get("/metadata/stats")
def get_interaction_stats(db: Session = Depends(get_db)):
    """Get interaction statistics."""
    return InteractionService.get_stats(db)


# AI-Powered Chat Endpoint
@router.post("/chat/log", response_model=ChatInteractionResponse)
def chat_log_interaction(data: ChatInteractionRequest):
    """Log an interaction via natural language chat with AI processing."""
    result = log_interaction(
        description=data.message,
        hcp_id=data.hcp_id if data.hcp_id else None,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to log interaction"))

    return {
        "interaction": result.get("interaction"),
        "summary": result.get("ai_summary", ""),
        "follow_up_suggestions": result.get("follow_up_suggestions", []),
        "extracted_entities": result.get("extracted_entities", {}),
    }


# AI Call Report Generation
@router.post("/reports/call", response_model=CallReportResponse)
def create_call_report(data: CallReportRequest):
    """Generate a structured call report for an interaction."""
    result = gen_report_tool(
        interaction_id=data.interaction_id,
        report_format=data.report_format,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to generate report"))

    return {
        "report": result.get("report", ""),
        "key_highlights": result.get("highlights", []),
        "recommendations": result.get("recommendations", []),
    }