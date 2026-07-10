# =============================================================================
# AI-First CRM HCP Module - HCP API Routes
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : FastAPI routes for HCP CRUD operations
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
FastAPI API routes for Healthcare Professional management.
Provides CRUD endpoints for HCP records.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.hcp import HCPCreate, HCPUpdate, HCPResponse, HCPListResponse
from app.services.hcp_service import HCPService

router = APIRouter(prefix="/hcps", tags=["HCPs"])


@router.post("", response_model=HCPResponse, status_code=201)
def create_hcp(data: HCPCreate, db: Session = Depends(get_db)):
    """Create a new Healthcare Professional."""
    hcp = HCPService.create(db, data)
    return hcp.to_dict()


@router.get("", response_model=HCPListResponse)
def list_hcps(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name or institution"),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    db: Session = Depends(get_db),
):
    """List all Healthcare Professionals with pagination and filtering."""
    skip = (page - 1) * page_size
    items, total = HCPService.get_all(
        db, skip=skip, limit=page_size, search=search, specialty=specialty
    )
    return {
        "items": [hcp.to_dict() for hcp in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{hcp_id}", response_model=HCPResponse)
def get_hcp(hcp_id: int, db: Session = Depends(get_db)):
    """Get a specific Healthcare Professional by ID."""
    hcp = HCPService.get_by_id(db, hcp_id)
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    return hcp.to_dict()


@router.put("/{hcp_id}", response_model=HCPResponse)
def update_hcp(hcp_id: int, data: HCPUpdate, db: Session = Depends(get_db)):
    """Update a Healthcare Professional."""
    hcp = HCPService.update(db, hcp_id, data)
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    return hcp.to_dict()


@router.delete("/{hcp_id}", status_code=204)
def delete_hcp(hcp_id: int, db: Session = Depends(get_db)):
    """Soft delete a Healthcare Professional."""
    success = HCPService.delete(db, hcp_id)
    if not success:
        raise HTTPException(status_code=404, detail="HCP not found")
    return None


@router.get("/search/by-name", response_model=list[HCPResponse])
def search_hcps(
    name: str = Query(..., min_length=1, description="Name to search for"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Search HCPs by name."""
    items = HCPService.search_by_name(db, name, limit)
    return [hcp.to_dict() for hcp in items]


@router.get("/metadata/specialties")
def get_specialties(db: Session = Depends(get_db)):
    """Get all unique specialties."""
    return {"specialties": HCPService.get_specialties(db)}


@router.get("/metadata/stats")
def get_hcp_stats(db: Session = Depends(get_db)):
    """Get HCP statistics."""
    return HCPService.get_stats(db)