"""Subject entity model — canonical representation of a study participant.

Implements: FR-015 (Subject Enrollment)
Aligns with: subject.json schema, 05-data-models/canonical/
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class SubjectStatus(str, Enum):
    """Lifecycle states for a study subject."""

    SCREENING = "screening"
    ENROLLED = "enrolled"
    ON_TREATMENT = "on_treatment"
    COMPLETED = "completed"
    DISCONTINUED = "discontinued"
    SCREEN_FAILED = "screen_failed"
    WITHDRAWN = "withdrawn"


class Subject(BaseModel):
    """Canonical Subject model.

    Represents a participant enrolled in a clinical study,
    including enrollment metadata and site assignment.
    """

    subject_id: UUID = Field(..., description="Unique subject identifier")
    study_id: UUID = Field(..., description="Reference to parent Study")
    site_id: UUID = Field(..., description="Enrolling site identifier")
    subject_number: str = Field(
        ..., min_length=1, max_length=20, description="Subject number within study"
    )
    status: SubjectStatus = Field(
        default=SubjectStatus.SCREENING, description="Current subject status"
    )
    screening_date: date | None = Field(
        default=None, description="Date of screening visit"
    )
    enrollment_date: date | None = Field(
        default=None, description="Date of formal enrollment"
    )
    date_of_birth: date | None = Field(
        default=None, description="Subject date of birth"
    )
    sex: str | None = Field(
        default=None, pattern=r"^(M|F|U)$", description="Biological sex (M/F/U)"
    )
    ethnicity: str | None = Field(
        default=None, max_length=100, description="Ethnicity"
    )
    race: str | None = Field(
        default=None, max_length=100, description="Race"
    )
    consent_date: date | None = Field(
        default=None, description="Date informed consent was signed"
    )
    discontinuation_reason: str | None = Field(
        default=None, max_length=500, description="Reason for discontinuation"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Record creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

    model_config = {"from_attributes": True, "json_schema_extra": {
        "examples": [
            {
                "subject_id": "770e8400-e29b-41d4-a716-446655440002",
                "study_id": "550e8400-e29b-41d4-a716-446655440000",
                "site_id": "880e8400-e29b-41d4-a716-446655440003",
                "subject_number": "CDOS-001-0001",
                "status": "enrolled",
            }
        ]
    }}
