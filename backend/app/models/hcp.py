# =============================================================================
# AI-First CRM HCP Module - HCP Model
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : Healthcare Professional database model
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
Healthcare Professional (HCP) model representing doctors,
physicians, and other healthcare providers in the CRM system.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, func
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.interaction import Interaction


class HCP(Base):
    """Healthcare Professional entity."""

    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=True)
    phone = Column(String(50), nullable=True)
    specialty = Column(String(200), nullable=True)
    institution = Column(String(300), nullable=True)
    location = Column(String(300), nullable=True)
    npi_number = Column(String(50), unique=True, nullable=True)  # National Provider Identifier
    tier = Column(String(50), default="general")  # Key Opinion Leader, General, etc.
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    interactions = relationship(
        "Interaction", back_populates="hcp", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<HCP(id={self.id}, name='{self.full_name}', specialty='{self.specialty}')>"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "specialty": self.specialty,
            "institution": self.institution,
            "location": self.location,
            "npi_number": self.npi_number,
            "tier": self.tier,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "interaction_count": len(self.interactions) if self.interactions else 0,
        }