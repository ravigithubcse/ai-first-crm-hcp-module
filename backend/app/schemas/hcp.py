# =============================================================================
# AI-First CRM HCP Module - HCP Schemas
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : Pydantic schemas for HCP data validation
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
Pydantic schemas for Healthcare Professional (HCP) data validation,
serialization, and API request/response models.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class HCPBase(BaseModel):
    """Base HCP schema with common fields."""
    full_name: str = Field(..., min_length=1, max_length=200, description="HCP full name")
    email: Optional[EmailStr] = Field(None, description="HCP email address")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone number")
    specialty: Optional[str] = Field(None, max_length=200, description="Medical specialty")
    institution: Optional[str] = Field(None, max_length=300, description="Hospital or clinic name")
    location: Optional[str] = Field(None, max_length=300, description="City, State")
    npi_number: Optional[str] = Field(None, max_length=50, description="National Provider Identifier")
    tier: str = Field(default="general", description="HCP tier: general, kol, influencer")
    notes: Optional[str] = Field(None, description="Additional notes")


class HCPCreate(HCPBase):
    """Schema for creating a new HCP."""
    pass


class HCPUpdate(BaseModel):
    """Schema for updating an existing HCP."""
    full_name: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    specialty: Optional[str] = Field(None, max_length=200)
    institution: Optional[str] = Field(None, max_length=300)
    location: Optional[str] = Field(None, max_length=300)
    npi_number: Optional[str] = Field(None, max_length=50)
    tier: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class HCPResponse(HCPBase):
    """Schema for HCP response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    interaction_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class HCPListResponse(BaseModel):
    """Schema for paginated HCP list response."""
    items: List[HCPResponse]
    total: int
    page: int
    page_size: int