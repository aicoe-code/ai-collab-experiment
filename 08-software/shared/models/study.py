"""Study entity model — canonical representation of a clinical trial.

Implements: FR-001 (Study Management)
Aligns with: study.json schema, 05-data-models/canonical/
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class StudyStatus(str, Enum):
    """Lifecycle states for a clinical study."""

    DRAFT = "draft"
    ACTIVATION_PENDING = "activation_pending"
    ENROLLING = "enrolling"
    ENROLLMENT_COMPLETE = "enrollment_complete"
    TREATMENT = "treatment"
    FOLLOW_UP = "follow_up"
    LOCKED = "locked"
    COMPLETED = "completed"
    TERMINATED = "terminated"


class Study(BaseModel):
    """Canonical Study model.

    Represents a clinical trial with protocol metadata,
    enrollment targets, and lifecycle status.
    """

    study_id: UUID = Field(..., description="Unique study identifier")
    protocol_number: str = Field(
        ..., min_length=1, max_length=50, description="Protocol number"
    )
    title: str = Field(
        ..., min_length=1, max_length=500, description="Full study title"
    )
    short_title: str = Field(
        ..., min_length=1, max_length=200, description="Abbreviated study title"
    )
    phase: str = Field(
        ..., pattern=r"^(I|II|III|IV|I/II|II/III|NA)$", description="Study phase"
    )
    status: StudyStatus = Field(
        default=StudyStatus.DRAFT, description="Current study lifecycle status"
    )
    sponsor_id: UUID = Field(..., description="Sponsor organization identifier")
    indication: str = Field(
        ..., min_length=1, max_length=300, description="Therapeutic indication"
    )
    target_enrollment: int = Field(
        ..., ge=0, description="Planned number of subjects"
    )
    actual_enrollment: int = Field(
        default=0, ge=0, description="Current enrolled subject count"
    )
    start_date: date | None = Field(default=None, description="Study start date")
    end_date: date | None = Field(default=None, description="Study end date")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Record creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

    model_config = {"from_attributes": True, "json_schema_extra": {
        "examples": [
            {
                "study_id": "550e8400-e29b-41d4-a716-446655440000",
                "protocol_number": "CDOS-2024-001",
                "title": "Phase III Trial of Compound X in Type 2 Diabetes",
                "short_title": "CDOS Compound X T2D",
                "phase": "III",
                "status": "enrolling",
                "sponsor_id": "660e8400-e29b-41d4-a716-446655440001",
                "indication": "Type 2 Diabetes Mellitus",
                "target_enrollment": 500,
            }
        ]
    }}
