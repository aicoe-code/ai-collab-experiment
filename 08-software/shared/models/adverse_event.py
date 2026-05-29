"""AdverseEvent entity model — canonical representation of an adverse event.

Implements: FR-020 (Safety Reporting)
Aligns with: adverse_event.json schema, 05-data-models/canonical/
Maps to SDTM AE domain.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class AdverseEventSeverity(str, Enum):
    """CTCAE severity grades.

    Aligned with: adverse_event.json severity enum, OpenAPI severity enum.
    """

    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    LIFE_THREATENING = "life_threatening"
    FATAL = "fatal"


class AdverseEventSeriousness(str, Enum):
    """ICH E2A seriousness criteria."""

    SERIOUS = "serious"
    NON_SERIOUS = "non_serious"


class AdverseEvent(BaseModel):
    """Canonical AdverseEvent model.

    Represents an adverse event reported during a clinical study.
    Maps to SDTM AE domain variables.
    """

    ae_id: UUID = Field(..., description="Unique adverse event identifier")
    subject_id: UUID = Field(..., description="Reference to affected Subject")
    study_id: UUID = Field(..., description="Reference to parent Study")
    site_id: UUID = Field(..., description="Site where event was reported")
    term: str = Field(
        ..., min_length=1, max_length=200, description="Reported adverse event term"
    )
    meddra_code: str | None = Field(
        default=None, max_length=20, description="MedDRA preferred term code"
    )
    severity: AdverseEventSeverity = Field(
        ..., description="CTCAE severity grade"
    )
    seriousness: AdverseEventSeriousness = Field(
        default=AdverseEventSeriousness.NON_SERIOUS,
        description="ICH seriousness classification",
    )
    onset_date: date = Field(..., description="Date of AE onset")
    resolution_date: date | None = Field(
        default=None, description="Date of AE resolution"
    )
    outcome: str | None = Field(
        default=None,
        max_length=100,
        description="Outcome (recovered, recovering, not recovered, fatal, unknown)",
    )
    causality: str | None = Field(
        default=None,
        max_length=100,
        description="Causality assessment (related, not related, unknown)",
    )
    is_sae: bool = Field(
        default=False, description="Whether event meets SAE criteria"
    )
    is_susar: bool = Field(
        default=False, description="Whether event is a SUSAR"
    )
    reported_to_regulator: bool = Field(
        default=False, description="Whether reported to regulatory authority"
    )
    narrative: str | None = Field(
        default=None, max_length=5000, description="Event narrative"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Record creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

    model_config = {"from_attributes": True}
