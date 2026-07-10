# =============================================================================
# AI-First CRM HCP Module - Follow-Up Schemas
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : Pydantic schemas for Follow-Up data validation
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
Pydantic schemas for Follow-Up action data validation,
serialization, and API request/response models.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class FollowUpBase(BaseModel):
    """Base follow-up schema with common fields."""
    interaction_id: int = Field(..., description="Associated interaction ID")
    title: str = Field(..., min_length=1, max_length=300, description="Follow-up title")
    description: Optional[str] = Field(None, description="Detailed description")
    due_date: Optional[datetime] = Field(None, description="Due date and time")
    priority: str = Field(default="medium", description="Priority: low, medium, high")
    assigned_to: Optional[str] = Field(None, description="Assigned representative")
    action_type: Optional[str] = Field(None, description="Type of follow-up action")


class FollowUpCreate(FollowUpBase):
    """Schema for creating a new follow-up."""
    ai_suggested: bool = Field(default=False, description="Whether AI suggested this")


class FollowUpUpdate(BaseModel):
    """Schema for updating an existing follow-up."""
    title: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = Field(None, description="Status: pending, completed, overdue")
    assigned_to: Optional[str] = None
    action_type: Optional[str] = None


class FollowUpResponse(FollowUpBase):
    """Schema for follow-up response."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    ai_suggested: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class FollowUpListResponse(BaseModel):
    """Schema for paginated follow-up list response."""
    items: List[FollowUpResponse]
    total: int
    page: int
    page_size: int


class ScheduleFollowUpRequest(BaseModel):
    """Schema for scheduling a follow-up via AI."""
    interaction_id: int = Field(..., description="Source interaction ID")
    title: str = Field(..., description="Follow-up title")
    description: Optional[str] = None
    due_date: Optional[datetime] = Field(None, description="When to schedule")
    priority: str = Field(default="medium")
    assigned_to: Optional[str] = None
    action_type: Optional[str] = None


class ScheduleFollowUpResponse(BaseModel):
    """Schema for schedule follow-up response."""
    follow_up: FollowUpResponse
    message: str = Field(..., description="Confirmation message")
    calendar_event: Optional[dict] = None