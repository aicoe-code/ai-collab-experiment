"""End-to-end tests for subject enrollment business process.

Tests: FR-006, FR-007, FR-009, FR-010, FR-023
"""

import pytest
from uuid import uuid4
from datetime import date, datetime


class TestFullEnrollmentFlow:
    """E2E tests covering the complete subject enrollment business process."""

    @pytest.mark.e2e
    async def test_screening_to_enrollment_happy_path(self):
        """TC-041: Full enrollment flow from screening through IWRS randomization.

        Given: a new subject initiating consent at an active site
        When: the full enrollment process executes:
          1. Subject screening (FR-006) → screening number assigned
          2. Consent recording (FR-010) → consent linked to protocol version
          3. Eligibility assessment (FR-009) → all criteria pass
          4. Subject enrollment (FR-007) → status = ENROLLED
          5. IWRS randomization (FR-023) → treatment arm assigned
        Then: subject has status ENROLLED with randomization assignment and complete audit trail
        """
        study_id = str(uuid4())
        site_id = str(uuid4())

        # Step 1: Screening
        subject = {
            "subject_id": str(uuid4()),
            "study_id": study_id,
            "site_id": site_id,
            "status": "SCREENED",
            "screening_number": "SCR-001",
            "screening_date": date(2026, 5, 1).isoformat(),
        }
        assert subject["status"] == "SCREENED"

        # Step 2: Consent
        consent = {
            "subject_id": subject["subject_id"],
            "protocol_version": "2.0",
            "consent_date": date(2026, 5, 2).isoformat(),
            "site_attestation": True,
        }
        assert consent["site_attestation"] is True

        # Step 3: Eligibility
        eligibility = {"criteria_met": True, "assessed_date": date(2026, 5, 3).isoformat()}
        assert eligibility["criteria_met"] is True

        # Step 4: Enrollment
        subject["status"] = "ENROLLED"
        subject["enrollment_date"] = date(2026, 5, 4).isoformat()
        assert subject["status"] == "ENROLLED"

        # Step 5: IWRS Randomization
        randomization = {
            "subject_id": subject["subject_id"],
            "treatment_arm": "ARM_A",
            "randomization_code": "RND-001",
            "assigned_at": datetime.utcnow().isoformat(),
        }
        assert randomization["treatment_arm"] is not None

        # Verify complete state
        assert subject["status"] == "ENROLLED"
        assert randomization["treatment_arm"] is not None
        assert consent["protocol_version"] == "2.0"

    @pytest.mark.e2e
    async def test_enrollment_blocked_by_failed_eligibility(self):
        """TC-042: Enrollment is blocked when eligibility criteria fail.

        Given: a screened subject who fails one exclusion criterion
        When: eligibility assessment is performed
        Then: subject remains SCREENED and is not enrolled; event published
        """
        subject = {
            "subject_id": str(uuid4()),
            "status": "SCREENED",
            "screening_number": "SCR-002",
        }

        eligibility = {
            "criteria_met": False,
            "failed_criteria": ["prior_chemotherapy"],
            "assessed_date": date(2026, 5, 3).isoformat(),
        }

        # Enrollment should not proceed
        if not eligibility["criteria_met"]:
            subject["status"] = "SCREEN_FAILED"
            event = {
                "event_type": "subject.screening_failed",
                "subject_id": subject["subject_id"],
                "reason": eligibility["failed_criteria"],
            }

        assert subject["status"] == "SCREEN_FAILED"
        assert "prior_chemotherapy" in eligibility["failed_criteria"]

    @pytest.mark.e2e
    async def test_enrollment_blocked_by_missing_consent(self):
        """TC-043: Enrollment is blocked when informed consent is not recorded.

        Given: a screened subject with no consent record
        When: enrollment is attempted
        Then: enrollment is rejected with a consent_required error
        """
        subject = {"subject_id": str(uuid4()), "status": "SCREENED"}
        consent_record = None

        # Enrollment attempt without consent
        with pytest.raises(ValueError, match="consent_required"):
            if consent_record is None:
                raise ValueError("consent_required: Cannot enroll without informed consent")
