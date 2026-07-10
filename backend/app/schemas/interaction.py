# =============================================================================
# AI-First CRM HCP Module - Interaction Schemas
# =============================================================================
# Author      : Ravi Kumar
# Date        : 2026-07-09
# Version     : 1.0.0
# Description : Pydantic schemas for Interaction data validation
# Copyright (c) 2026. All rights reserved.
# =============================================================================

"""
Pydantic schemas for HCP Interaction data validation,
serialization, and API request/response models.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class InteractionBase(BaseModel):
    """Base interaction schema with common fields."""
    hcp_id: int = Field(..., description="Associated HCP ID")
    interaction_type: str = Field(default="Meeting", description="Type of interaction")
    date: datetime = Field(..., description="Interaction date and time")
    time: Optional[str] = Field(None, description="Time of interaction (HH:MM)")
    attendees: List[str] = Field(default_factory=list, description="List of attendees")
    topics_discussed: Optional[str] = Field(None, description="Key discussion points")
    materials_shared: List[str] = Field(default_factory=list, description="Shared materials")
    samples_distributed: List[str] = Field(default_factory=list, description="Distributed samples")
    sentiment: str = Field(default="neutral", description="HCP sentiment")
    outcomes: Optional[str] = Field(None, description="Key outcomes or agreements")
    next_steps: Optional[str] = Field(None, description="Next steps or tasks")
    logged_by: Optional[str] = Field(None, description="Representative name")
    source: str = Field(default="form", description="Source: form, chat, voice")


class InteractionCreate(InteractionBase):
    """Schema for creating a new interaction."""
    voice_note_transcript: Optional[str] = Field(None, description="Voice note transcript")


class InteractionUpdate(BaseModel):
    """Schema for updating an existing interaction."""
    hcp_id: Optional[int] = None
    interaction_type: Optional[str] = None
    date: Optional[datetime] = None
    time: Optional[str] = None
    attendees: Optional[List[str]] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[List[str]] = None
    samples_distributed: Optional[List[str]] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    next_steps: Optional[str] = None
    voice_note_transcript: Optional[str] = None
    logged_by: Optional[str] = None
    source: Optional[str] = None


class InteractionResponse(InteractionBase):
    """Schema for interaction response with AI-generated fields."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    summary: Optional[str] = Field(None, description="AI-generated summary")
    key_insights: List[str] = Field(default_factory=list, description="AI-extracted insights")
    follow_up_actions: List[str] = Field(default_factory=list, description="AI-suggested follow-ups")
    voice_note_url: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class InteractionListResponse(BaseModel):
    """Schema for paginated interaction list response."""
    items: List[InteractionResponse]
    total: int
    page: int
    page_size: int


class ChatInteractionRequest(BaseModel):
    """Schema for logging an interaction via chat."""
    message: str = Field(..., min_length=1, description="Natural language interaction description")
    hcp_id: Optional[int] = Field(None, description="Optional HCP ID if known")


class ChatInteractionResponse(BaseModel):
    """Schema for chat interaction response."""
    interaction: Optional[InteractionResponse] = None
    summary: str = Field(..., description="AI summary of the interaction")
    follow_up_suggestions: List[str] = Field(default_factory=list)
    extracted_entities: dict = Field(default_factory=dict)


class CallReportRequest(BaseModel):
    """Schema for generating a call report."""
    interaction_id: int = Field(..., description="Interaction ID to generate report for")
    report_format: str = Field(default="structured", description="Report format")


class CallReportResponse(BaseModel):
    """Schema for call report response."""
    report: str = Field(..., description="Generated call report")
    key_highlights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)