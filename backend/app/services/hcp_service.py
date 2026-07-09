# =============================================================================
# AI-First CRM HCP Module - HCP Service
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : Business logic for HCP management
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
HCP Service layer containing business logic for
Healthcare Professional CRUD operations and queries.
"""

from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.hcp import HCP
from app.schemas.hcp import HCPCreate, HCPUpdate


class HCPService:
    """Service class for HCP operations."""

    @staticmethod
    def create(db: Session, data: HCPCreate) -> HCP:
        """Create a new HCP record."""
        hcp = HCP(**data.model_dump())
        db.add(hcp)
        db.commit()
        db.refresh(hcp)
        return hcp

    @staticmethod
    def get_by_id(db: Session, hcp_id: int) -> Optional[HCP]:
        """Get HCP by ID."""
        return db.query(HCP).filter(HCP.id == hcp_id).first()

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        specialty: Optional[str] = None,
    ) -> tuple[List[HCP], int]:
        """Get all HCPs with optional filtering and pagination."""
        query = db.query(HCP).filter(HCP.is_active == True)

        if search:
            query = query.filter(
                HCP.full_name.ilike(f"%{search}%") |
                HCP.institution.ilike(f"%{search}%")
            )

        if specialty:
            query = query.filter(HCP.specialty.ilike(f"%{specialty}%"))

        total = query.count()
        items = query.order_by(HCP.full_name).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(db: Session, hcp_id: int, data: HCPUpdate) -> Optional[HCP]:
        """Update an existing HCP record."""
        hcp = HCPService.get_by_id(db, hcp_id)
        if not hcp:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(hcp, field, value)

        db.commit()
        db.refresh(hcp)
        return hcp

    @staticmethod
    def delete(db: Session, hcp_id: int) -> bool:
        """Soft delete an HCP by setting is_active to False."""
        hcp = HCPService.get_by_id(db, hcp_id)
        if not hcp:
            return False

        hcp.is_active = False
        db.commit()
        return True

    @staticmethod
    def search_by_name(db: Session, name: str, limit: int = 10) -> List[HCP]:
        """Search HCPs by name."""
        return (
            db.query(HCP)
            .filter(
                HCP.full_name.ilike(f"%{name}%"),
                HCP.is_active == True,
            )
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_specialties(db: Session) -> List[str]:
        """Get all unique specialties."""
        result = db.query(HCP.specialty).distinct().all()
        return [s[0] for s in result if s[0]]

    @staticmethod
    def get_stats(db: Session) -> dict:
        """Get HCP statistics."""
        total = db.query(func.count(HCP.id)).filter(HCP.is_active == True).scalar()
        by_tier = (
            db.query(HCP.tier, func.count(HCP.id))
            .filter(HCP.is_active == True)
            .group_by(HCP.tier)
            .all()
        )
        return {
            "total": total,
            "by_tier": {tier: count for tier, count in by_tier},
        }