"""
Pydantic schemas for Connection Recommendation (User-to-User Networking).
"""

import uuid
from datetime import datetime
from typing import TypedDict

from pydantic import BaseModel, ConfigDict, Field


class UserProfileDict(TypedDict):
    """Profile information extracted for a real registered user."""
    user_id: str
    email: str
    full_name: str
    avatar: str | None
    profession: str | None
    company: str | None
    location: str | None
    skills: list[str]
    interests: list[str]
    current_needs: list[str]  # Looking for
    current_offers: list[str]  # Offering
    summary: str | None


class ConnectionRecommendation(BaseModel):
    """
    Connection recommendation data recommending a real user to the current user.
    """
    id: uuid.UUID
    owner_user_id: uuid.UUID
    target_user_id: uuid.UUID | None = None
    reason: str
    priority: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    confidence: float = 0.5   # 0.0 - 1.0
    status: str = "PENDING"   # PENDING, ACCEPTED, REJECTED, DISMISSED
    created_at: datetime
    expires_at: datetime | None = None

    # Real Target User details
    target_user_name: str | None = None
    target_user_email: str | None = None
    target_user_avatar: str | None = None
    target_user_profession: str | None = None
    target_user_company: str | None = None
    target_user_location: str | None = None
    target_user_skills: list[str] = Field(default_factory=list)
    target_user_interests: list[str] = Field(default_factory=list)
    target_user_needs: list[str] = Field(default_factory=list)
    target_user_offers: list[str] = Field(default_factory=list)

    # Legacy fields for backward compatibility if any old contacts exist
    contact_id: uuid.UUID | None = None
    target_contact_id: uuid.UUID | None = None
    contact_name: str | None = None
    target_contact_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ConnectionRecommendationDetail(BaseModel):
    """
    Detailed view of a recommendation comparing Current User and Target User.
    """
    id: uuid.UUID
    reason: str
    priority: str
    confidence: float
    status: str
    created_at: datetime

    # Current User (You)
    current_user_id: uuid.UUID
    current_user_name: str
    current_user_email: str | None = None
    current_user_profession: str | None = None
    current_user_company: str | None = None
    current_user_location: str | None = None
    current_user_skills: list[str] = Field(default_factory=list)
    current_user_interests: list[str] = Field(default_factory=list)
    current_user_needs: list[str] = Field(default_factory=list)    # Looking for
    current_user_offers: list[str] = Field(default_factory=list)   # Offering

    # Target User (The Person to Connect With)
    target_user_id: uuid.UUID
    target_user_name: str
    target_user_email: str | None = None
    target_user_avatar: str | None = None
    target_user_profession: str | None = None
    target_user_company: str | None = None
    target_user_location: str | None = None
    target_user_skills: list[str] = Field(default_factory=list)
    target_user_interests: list[str] = Field(default_factory=list)
    target_user_needs: list[str] = Field(default_factory=list)     # Looking for
    target_user_offers: list[str] = Field(default_factory=list)    # Offering

    # Suggested message & conversation link
    suggested_intro: str | None = None
    conversation_id: uuid.UUID | None = None

    # Legacy alias fields for backwards compatibility
    contact_a_id: uuid.UUID | None = None
    contact_a_name: str | None = None
    contact_a_profession: str | None = None
    contact_a_company: str | None = None
    contact_a_interests: list[str] = Field(default_factory=list)
    contact_a_needs: list[str] = Field(default_factory=list)

    contact_b_id: uuid.UUID | None = None
    contact_b_name: str | None = None
    contact_b_profession: str | None = None
    contact_b_company: str | None = None
    contact_b_interests: list[str] = Field(default_factory=list)
    contact_b_offers: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AcceptConnectionRequest(BaseModel):
    """Request to accept a connection recommendation."""
    custom_message: str | None = Field(
        default=None,
        max_length=1000,
        description="Custom message to send as the first chat message"
    )


class GenerateConnectionsResponse(BaseModel):
    """Response from generating connection recommendations."""
    generated: int
    total_pending: int
    message: str
