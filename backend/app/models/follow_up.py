# =============================================================================
# AI-First CRM HCP Module - Follow-Up Model
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : Follow-up action database model
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
FollowUp model representing scheduled follow-up actions
generated from HCP interactions.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.interaction import Interaction


class FollowUp(Base):
    """Follow-up action entity."""

    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    interaction_id = Column(
        Integer,
        ForeignKey("interactions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Follow-up Details
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    priority = Column(String(50), default="medium")  # low, medium, high
    status = Column(String(50), default="pending")  # pending, completed, overdue
    assigned_to = Column(String(200), nullable=True)
    action_type = Column(String(100), nullable=True)  # email, meeting, call, send_material

    # AI-Generated
    ai_suggested = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    interaction: "Interaction" = relationship("Interaction", back_populates="follow_ups")

    def __repr__(self) -> str:
        return f"<FollowUp(id={self.id}, title='{self.title}', status='{self.status}')>"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "interaction_id": self.interaction_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "action_type": self.action_type,
            "ai_suggested": self.ai_suggested,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }