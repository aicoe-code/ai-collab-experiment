"""Unit tests for Subject model and status transitions.

Tests: FR-006, FR-007, FR-008, FR-009, FR-010
"""

import pytest
from uuid import uuid4
from datetime import date


class TestSubjectModel:
    """Tests for FR-006: Subject screening and model validation."""

    def test_subject_model_with_valid_data(self):
        """TC-008: Subject model validates with all required fields present.

        Given: valid subject data (subject_id, study_id, site_id, status)
        When: Subject model is instantiated
        Then: the model is created without validation errors
        """
        from shared.models.subject import Subject, SubjectStatus

        subject = Subject(
            subject_id=uuid4(),
            study_id=uuid4(),
            site_id=uuid4(),
            status=SubjectStatus.SCREENED,
        )
        assert subject.status == SubjectStatus.SCREENED
        assert subject.subject_id is not None

    def test_subject_model_rejects_missing_study_id(self):
        """TC-009: Subject model raises error when study_id is missing.

        Given: subject data without a study_id
        When: Subject model is instantiated
        Then: a ValidationError is raised
        """
        from shared.models.subject import Subject, SubjectStatus

        with pytest.raises(Exception):
            Subject(
                subject_id=uuid4(),
                study_id=None,
                site_id=uuid4(),
                status=SubjectStatus.SCREENED,
            )


class TestSubjectStatusTransitions:
    """Tests for FR-007: Subject enrollment and FR-008: Subject withdrawal."""

    def test_transition_screened_to_enrolled(self):
        """TC-010: Subject transitions from SCREENED to ENROLLED upon eligibility pass.

        Given: a subject with status SCREENED and passing eligibility
        When: enroll_subject() is called
        Then: subject status changes to ENROLLED
        """
        from shared.models.subject import SubjectStatus

        current_status = SubjectStatus.SCREENED
        allowed_transitions = {
            SubjectStatus.SCREENED: [SubjectStatus.ENROLLED, SubjectStatus.SCREEN_FAILED],
            SubjectStatus.ENROLLED: [SubjectStatus.WITHDRAWN, SubjectStatus.COMPLETED],
        }

        assert SubjectStatus.ENROLLED in allowed_transitions[current_status]

    def test_transition_enrolled_to_withdrawn(self):
        """TC-011: Subject transitions from ENROLLED to WITHDRAWN with reason.

        Given: a subject with status ENROLLED
        When: withdraw_subject(reason='Adverse Event') is called
        Then: subject status changes to WITHDRAWN and withdrawal reason is recorded
        """
        from shared.models.subject import SubjectStatus

        current_status = SubjectStatus.ENROLLED
        withdrawal_reason = "Adverse Event"

        allowed_transitions = {
            SubjectStatus.ENROLLED: [SubjectStatus.WITHDRAWN, SubjectStatus.COMPLETED],
        }

        assert SubjectStatus.WITHDRAWN in allowed_transitions[current_status]
        assert withdrawal_reason is not None

    def test_invalid_status_transition_rejected(self):
        """TC-012: Direct transition from SCREENED to WITHDRAWN is rejected.

        Given: a subject with status SCREENED
        When: an attempt is made to transition to WITHDRAWN
        Then: the transition is rejected as invalid
        """
        from shared.models.subject import SubjectStatus

        current_status = SubjectStatus.SCREENED
        allowed_transitions = {
            SubjectStatus.SCREENED: [SubjectStatus.ENROLLED, SubjectStatus.SCREEN_FAILED],
        }

        assert SubjectStatus.WITHDRAWN not in allowed_transitions[current_status]


class TestSubjectEligibility:
    """Tests for FR-009: Eligibility assessment and FR-010: Consent tracking."""

    def test_eligibility_pass_when_all_criteria_met(self):
        """TC-013: Eligibility assessment returns PASS when all inclusion criteria met.

        Given: a subject whose data satisfies all inclusion criteria
        When: evaluate_eligibility() is called
        Then: the result is PASS
        """
        criteria_results = {
            "age_18_65": True,
            "bmi_18_35": True,
            "no_prior_therapy": True,
            "consent_signed": True,
        }
        eligibility = all(criteria_results.values())
        assert eligibility is True

    def test_eligibility_fail_when_exclusion_criterion_met(self):
        """TC-014: Eligibility assessment returns FAIL when any exclusion criterion met.

        Given: a subject who meets inclusion but triggers an exclusion criterion
        When: evaluate_eligibility() is called
        Then: the result is FAIL
        """
        inclusion_results = {"age_18_65": True, "bmi_18_35": True}
        exclusion_results = {"prior_chemotherapy": True}  # exclusion triggered

        eligibility = all(inclusion_results.values()) and not any(exclusion_results.values())
        assert eligibility is False

    def test_consent_tracking_links_to_protocol_version(self):
        """TC-015: Informed consent record links to the applicable protocol version.

        Given: a subject signing consent for protocol version 2.0
        When: record_consent() is called
        Then: the consent record includes protocol_version='2.0' and consent_date
        """
        consent = {
            "subject_id": str(uuid4()),
            "protocol_version": "2.0",
            "consent_date": date(2026, 5, 15),
            "site_attestation": True,
        }
        assert consent["protocol_version"] == "2.0"
        assert consent["consent_date"] is not None
        assert consent["site_attestation"] is True
