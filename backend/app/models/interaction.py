# =============================================================================
# AI-First CRM HCP Module - Interaction Model
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : HCP Interaction database model
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
Interaction model representing meetings, calls, and other
engagements between field representatives and HCPs.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey,
    JSON, Float, func
)
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.hcp import HCP
    from app.models.follow_up import FollowUp


class Interaction(Base):
    """HCP Interaction entity."""

    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    hcp_id = Column(Integer, ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False, index=True)

    # Interaction Details
    interaction_type = Column(String(100), nullable=False)  # Meeting, Call, Email, etc.
    date = Column(DateTime(timezone=True), nullable=False)
    time = Column(String(10), nullable=True)
    attendees = Column(JSON, default=list)  # List of attendee names
    topics_discussed = Column(Text, nullable=True)
    materials_shared = Column(JSON, default=list)  # List of materials
    samples_distributed = Column(JSON, default=list)  # List of samples

    # AI-Generated Fields
    sentiment = Column(String(50), default="neutral")  # positive, neutral, negative
    summary = Column(Text, nullable=True)  # AI-generated summary
    key_insights = Column(JSON, default=list)  # AI-extracted insights
    follow_up_actions = Column(JSON, default=list)  # AI-suggested follow-ups

    # Outcomes
    outcomes = Column(Text, nullable=True)
    next_steps = Column(Text, nullable=True)

    # Voice Note
    voice_note_transcript = Column(Text, nullable=True)
    voice_note_url = Column(String(500), nullable=True)

    # Metadata
    logged_by = Column(String(200), nullable=True)  # Representative name
    source = Column(String(50), default="form")  # form, chat, voice
    confidence_score = Column(Float, nullable=True)  # AI confidence

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    hcp = relationship("HCP", back_populates="interactions")
    follow_ups = relationship(
        "FollowUp", back_populates="interaction", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Interaction(id={self.id}, hcp_id={self.hcp_id}, type='{self.interaction_type}')>"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "hcp_id": self.hcp_id,
            "interaction_type": self.interaction_type,
            "date": self.date.isoformat() if self.date else None,
            "time": self.time,
            "attendees": self.attendees or [],
            "topics_discussed": self.topics_discussed,
            "materials_shared": self.materials_shared or [],
            "samples_distributed": self.samples_distributed or [],
            "sentiment": self.sentiment,
            "summary": self.summary,
            "key_insights": self.key_insights or [],
            "follow_up_actions": self.follow_up_actions or [],
            "outcomes": self.outcomes,
            "next_steps": self.next_steps,
            "voice_note_transcript": self.voice_note_transcript,
            "voice_note_url": self.voice_note_url,
            "logged_by": self.logged_by,
            "source": self.source,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }