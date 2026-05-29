"""LabResult entity model — canonical representation of a laboratory test result.

Implements: FR-018 (Lab Data Management)
Aligns with: lab_result.json schema, 05-data-models/canonical/
Maps to SDTM LB domain.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class LabResultStatus(str, Enum):
    """Status of a lab result record."""

    PENDING = "pending"
    RECEIVED = "received"
    VERIFIED = "verified"
    QUERY = "query"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class LabResult(BaseModel):
    """Canonical LabResult model.

    Represents a laboratory test result for a subject,
    including specimen metadata and reference ranges.
    Maps to SDTM LB domain variables.
    """

    lab_result_id: UUID = Field(..., description="Unique lab result identifier")
    subject_id: UUID = Field(..., description="Reference to Subject")
    study_id: UUID = Field(..., description="Reference to parent Study")
    site_id: UUID = Field(..., description="Collection site identifier")
    visit_name: str = Field(
        ..., max_length=50, description="Study visit when sample was collected"
    )
    specimen_type: str = Field(
        ..., max_length=100, description="Type of specimen (blood, urine, etc.)"
    )
    test_name: str = Field(
        ..., max_length=200, description="Laboratory test name"
    )
    test_code: str = Field(
        ..., max_length=50, description="Laboratory test code"
    )
    result_value: str = Field(
        ..., max_length=100, description="Result value (numeric or text)"
    )
    unit: str | None = Field(
        default=None, max_length=50, description="Unit of measurement"
    )
    reference_range_low: str | None = Field(
        default=None, max_length=50, description="Lower limit of normal range"
    )
    reference_range_high: str | None = Field(
        default=None, max_length=50, description="Upper limit of normal range"
    )
    normal_flag: str | None = Field(
        default=None,
        pattern=r"^(NORMAL|HIGH|LOW|ABNORMAL|ND)?$",
        description="Normal range flag",
    )
    collection_date: date = Field(
        ..., description="Date specimen was collected"
    )
    collection_time: str | None = Field(
        default=None, max_length=20, description="Time specimen was collected (HH:MM)"
    )
    status: LabResultStatus = Field(
        default=LabResultStatus.PENDING, description="Result verification status"
    )
    lab_name: str | None = Field(
        default=None, max_length=200, description="Performing laboratory name"
    )
    comments: str | None = Field(
        default=None, max_length=1000, description="Result comments"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Record creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

    model_config = {"from_attributes": True}
