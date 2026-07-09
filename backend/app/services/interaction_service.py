# =============================================================================
# AI-First CRM HCP Module - Interaction Service
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : Business logic for Interaction management
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
Interaction Service layer containing business logic for
HCP Interaction CRUD operations, queries, and AI integration.
"""

from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.interaction import Interaction
from app.models.hcp import HCP
from app.schemas.interaction import InteractionCreate, InteractionUpdate


class InteractionService:
    """Service class for Interaction operations."""

    @staticmethod
    def create(db: Session, data: InteractionCreate) -> Interaction:
        """Create a new interaction record."""
        interaction = Interaction(**data.model_dump())
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return interaction

    @staticmethod
    def get_by_id(db: Session, interaction_id: int) -> Optional[Interaction]:
        """Get interaction by ID."""
        return db.query(Interaction).filter(Interaction.id == interaction_id).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        hcp_id: Optional[int] = None,
        interaction_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[List[Interaction], int]:
        """Get all interactions with optional filtering and pagination."""
        query = db.query(Interaction)

        if hcp_id:
            query = query.filter(Interaction.hcp_id == hcp_id)

        if interaction_type:
            query = query.filter(Interaction.interaction_type == interaction_type)

        if start_date:
            query = query.filter(Interaction.date >= start_date)

        if end_date:
            query = query.filter(Interaction.date <= end_date)

        total = query.count()
        items = query.order_by(Interaction.date.desc()).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(
        db: Session, interaction_id: int, data: InteractionUpdate
    ) -> Optional[Interaction]:
        """Update an existing interaction record."""
        interaction = InteractionService.get_by_id(db, interaction_id)
        if not interaction:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(interaction, field, value)

        db.commit()
        db.refresh(interaction)
        return interaction

    @staticmethod
    def delete(db: Session, interaction_id: int) -> bool:
        """Permanently delete an interaction."""
        interaction = InteractionService.get_by_id(db, interaction_id)
        if not interaction:
            return False

        db.delete(interaction)
        db.commit()
        return True

    @staticmethod
    def get_by_hcp(db: Session, hcp_id: int, limit: int = 50) -> List[Interaction]:
        """Get all interactions for a specific HCP."""
        return (
            db.query(Interaction)
            .filter(Interaction.hcp_id == hcp_id)
            .order_by(Interaction.date.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_recent(db: Session, limit: int = 10) -> List[Interaction]:
        """Get recent interactions across all HCPs."""
        return (
            db.query(Interaction)
            .order_by(Interaction.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_stats(db: Session) -> dict:
        """Get interaction statistics."""
        total = db.query(func.count(Interaction.id)).scalar()
        by_type = (
            db.query(Interaction.interaction_type, func.count(Interaction.id))
            .group_by(Interaction.interaction_type)
            .all()
        )
        by_sentiment = (
            db.query(Interaction.sentiment, func.count(Interaction.id))
            .group_by(Interaction.sentiment)
            .all()
        )
        return {
            "total": total,
            "by_type": {t: c for t, c in by_type},
            "by_sentiment": {s: c for s, c in by_sentiment},
        }

    @staticmethod
    def update_ai_fields(
        db: Session,
        interaction_id: int,
        summary: str,
        key_insights: list,
        follow_up_actions: list,
        confidence_score: Optional[float] = None,
    ) -> Optional[Interaction]:
        """Update AI-generated fields on an interaction."""
        interaction = InteractionService.get_by_id(db, interaction_id)
        if not interaction:
            return None

        interaction.summary = summary
        interaction.key_insights = key_insights
        interaction.follow_up_actions = follow_up_actions
        if confidence_score is not None:
            interaction.confidence_score = confidence_score

        db.commit()
        db.refresh(interaction)
        return interaction