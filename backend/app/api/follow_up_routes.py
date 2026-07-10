# =============================================================================
# AI-First CRM HCP Module - Follow-Up API Routes
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : FastAPI routes for Follow-Up CRUD operations
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
FastAPI API routes for Follow-Up action management.
Provides CRUD endpoints and AI-powered scheduling.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.follow_up import (
    FollowUpCreate,
    FollowUpUpdate,
    FollowUpResponse,
    FollowUpListResponse,
    ScheduleFollowUpRequest,
    ScheduleFollowUpResponse,
)
from app.services.follow_up_service import FollowUpService
from app.services.interaction_service import InteractionService
from app.langgraph_tools.schedule_followup import schedule_follow_up as schedule_tool

router = APIRouter(prefix="/follow-ups", tags=["Follow-Ups"])


@router.post("", response_model=FollowUpResponse, status_code=201)
def create_follow_up(data: FollowUpCreate, db: Session = Depends(get_db)):
    """Create a new follow-up action."""
    # Verify interaction exists
    interaction = InteractionService.get_by_id(db, data.interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    follow_up = FollowUpService.create(db, data)
    return follow_up.to_dict()


@router.get("", response_model=FollowUpListResponse)
def list_follow_ups(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    interaction_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List follow-ups with pagination and filtering."""
    skip = (page - 1) * page_size
    items, total = FollowUpService.get_all(
        db, skip=skip, limit=page_size, interaction_id=interaction_id, status=status
    )
    return {
        "items": [f.to_dict() for f in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{follow_up_id}", response_model=FollowUpResponse)
def get_follow_up(follow_up_id: int, db: Session = Depends(get_db)):
    """Get a specific follow-up by ID."""
    follow_up = FollowUpService.get_by_id(db, follow_up_id)
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return follow_up.to_dict()


@router.put("/{follow_up_id}", response_model=FollowUpResponse)
def update_follow_up(
    follow_up_id: int, data: FollowUpUpdate, db: Session = Depends(get_db)
):
    """Update a follow-up."""
    follow_up = FollowUpService.update(db, follow_up_id, data)
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return follow_up.to_dict()


@router.post("/{follow_up_id}/complete", response_model=FollowUpResponse)
def complete_follow_up(follow_up_id: int, db: Session = Depends(get_db)):
    """Mark a follow-up as completed."""
    follow_up = FollowUpService.complete(db, follow_up_id)
    if not follow_up:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return follow_up.to_dict()


@router.delete("/{follow_up_id}", status_code=204)
def delete_follow_up(follow_up_id: int, db: Session = Depends(get_db)):
    """Delete a follow-up."""
    success = FollowUpService.delete(db, follow_up_id)
    if not success:
        raise HTTPException(status_code=404, detail="Follow-up not found")
    return None


@router.get("/interaction/{interaction_id}")
def get_interaction_follow_ups(interaction_id: int, db: Session = Depends(get_db)):
    """Get all follow-ups for a specific interaction."""
    items = FollowUpService.get_by_interaction(db, interaction_id)
    return {
        "items": [f.to_dict() for f in items],
        "total": len(items),
    }


@router.get("/pending/all")
def get_pending_follow_ups(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Get all pending follow-ups."""
    items = FollowUpService.get_pending(db, limit)
    return {
        "items": [f.to_dict() for f in items],
        "total": len(items),
    }


@router.get("/metadata/stats")
def get_follow_up_stats(db: Session = Depends(get_db)):
    """Get follow-up statistics."""
    return FollowUpService.get_stats(db)


# AI-Powered Schedule Follow-Up
@router.post("/schedule/ai", response_model=ScheduleFollowUpResponse)
def ai_schedule_follow_up(data: ScheduleFollowUpRequest):
    """Schedule a follow-up using AI-powered suggestions."""
    result = schedule_tool(
        interaction_id=data.interaction_id,
        title=data.title,
        description=data.description or "",
        due_date=data.due_date.strftime("%Y-%m-%d") if data.due_date else "",
        priority=data.priority,
        assigned_to=data.assigned_to or "",
        action_type=data.action_type or "",
        auto_generate=True,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to schedule follow-up"))

    return {
        "follow_up": result.get("follow_up", {}),
        "message": result.get("message", ""),
        "calendar_event": result.get("calendar_event", {}),
    }