# =============================================================================
# AI-First CRM HCP Module - Follow-Up Service
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : Business logic for Follow-Up management
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
Follow-Up Service layer containing business logic for
follow-up action CRUD operations and scheduling.
"""

from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.follow_up import FollowUp
from app.schemas.follow_up import FollowUpCreate, FollowUpUpdate


class FollowUpService:
    """Service class for Follow-Up operations."""

    @staticmethod
    def create(db: Session, data: FollowUpCreate) -> FollowUp:
        """Create a new follow-up record."""
        follow_up = FollowUp(**data.model_dump())
        db.add(follow_up)
        db.commit()
        db.refresh(follow_up)
        return follow_up

    @staticmethod
    def get_by_id(db: Session, follow_up_id: int) -> Optional[FollowUp]:
        """Get follow-up by ID."""
        return db.query(FollowUp).filter(FollowUp.id == follow_up_id).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        interaction_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> tuple[List[FollowUp], int]:
        """Get all follow-ups with optional filtering."""
        query = db.query(FollowUp)

        if interaction_id:
            query = query.filter(FollowUp.interaction_id == interaction_id)

        if status:
            query = query.filter(FollowUp.status == status)

        total = query.count()
        items = query.order_by(FollowUp.due_date.asc()).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(
        db: Session, follow_up_id: int, data: FollowUpUpdate
    ) -> Optional[FollowUp]:
        """Update an existing follow-up."""
        follow_up = FollowUpService.get_by_id(db, follow_up_id)
        if not follow_up:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(follow_up, field, value)

        db.commit()
        db.refresh(follow_up)
        return follow_up

    @staticmethod
    def complete(db: Session, follow_up_id: int) -> Optional[FollowUp]:
        """Mark a follow-up as completed."""
        follow_up = FollowUpService.get_by_id(db, follow_up_id)
        if not follow_up:
            return None

        follow_up.status = "completed"
        follow_up.completed_at = datetime.now()
        db.commit()
        db.refresh(follow_up)
        return follow_up

    @staticmethod
    def delete(db: Session, follow_up_id: int) -> bool:
        """Delete a follow-up."""
        follow_up = FollowUpService.get_by_id(db, follow_up_id)
        if not follow_up:
            return False

        db.delete(follow_up)
        db.commit()
        return True

    @staticmethod
    def get_pending(db: Session, limit: int = 50) -> List[FollowUp]:
        """Get pending follow-ups."""
        return (
            db.query(FollowUp)
            .filter(FollowUp.status == "pending")
            .order_by(FollowUp.due_date.asc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_interaction(db: Session, interaction_id: int) -> List[FollowUp]:
        """Get all follow-ups for a specific interaction."""
        return (
            db.query(FollowUp)
            .filter(FollowUp.interaction_id == interaction_id)
            .order_by(FollowUp.created_at.desc())
            .all()
        )

    @staticmethod
    def get_stats(db: Session) -> dict:
        """Get follow-up statistics."""
        total = db.query(func.count(FollowUp.id)).scalar()
        by_status = (
            db.query(FollowUp.status, func.count(FollowUp.id))
            .group_by(FollowUp.status)
            .all()
        )
        by_priority = (
            db.query(FollowUp.priority, func.count(FollowUp.id))
            .group_by(FollowUp.priority)
            .all()
        )
        return {
            "total": total,
            "by_status": {s: c for s, c in by_status},
            "by_priority": {p: c for p, c in by_priority},
        }