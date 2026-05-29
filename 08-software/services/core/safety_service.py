"""Safety Service — core business logic for adverse event management.

Implements: FR-020 (Safety Reporting), FR-021 (SUSAR Detection)
Aligns with: ICH E2A, MedDRA coding, Safety system integration
"""

from __future__ import annotations

from uuid import UUID, uuid4
from datetime import datetime

from shared.models.adverse_event import (
    AdverseEvent,
    AdverseEventSeverity,
    AdverseEventSeriousness,
)
from shared.utils.logging import get_logger
from shared.utils.errors import NotFoundError, ValidationError

logger = get_logger(__name__)

# SUSAR detection rules: certain severity + seriousness combinations
_SUSAR_SEVERITY_THRESHOLD = {
    AdverseEventSeriousness.SERIOUS: {
        AdverseEventSeverity.LIFE_THREATENING,
        AdverseEventSeverity.FATAL,
    },
}


class SafetyService:
    """Service for adverse event management and safety signal detection.

    Handles AE reporting, SUSAR detection, and regulatory reporting workflows.
    """

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize safety service.

        Args:
            db_session: Async database session (SQLAlchemy AsyncSession).
        """
        self._db = db_session

    async def report_adverse_event(
        self,
        subject_id: UUID,
        study_id: UUID,
        site_id: UUID,
        term: str,
        severity: AdverseEventSeverity,
        onset_date: str,
        seriousness: AdverseEventSeriousness = AdverseEventSeriousness.NON_SERIOUS,
        meddra_code: str | None = None,
        narrative: str | None = None,
        causality: str | None = None,
    ) -> AdverseEvent:
        """Report a new adverse event.

        Implements: FR-020, TC-060

        Args:
            subject_id: Affected subject UUID.
            study_id: Parent study UUID.
            site_id: Reporting site UUID.
            term: Reported AE term.
            severity: CTCAE severity grade.
            onset_date: Date of AE onset (ISO format string).
            seriousness: ICH seriousness classification.
            meddra_code: MedDRA preferred term code.
            narrative: Event narrative.
            causality: Causality assessment.

        Returns:
            Newly created AdverseEvent instance.
        """
        from datetime import date as date_type

        logger.info(
            "Reporting AE '%s' for subject %s (severity=%s, seriousness=%s)",
            term, subject_id, severity.value, seriousness.value,
        )

        ae = AdverseEvent(
            ae_id=uuid4(),
            subject_id=subject_id,
            study_id=study_id,
            site_id=site_id,
            term=term,
            meddra_code=meddra_code,
            severity=severity,
            seriousness=seriousness,
            onset_date=date_type.fromisoformat(onset_date),
            causality=causality,
            narrative=narrative,
            is_susar=False,
            reported_to_regulator=False,
        )

        # SUSAR detection
        ae.is_susar = self._detect_susar(ae)
        if ae.is_susar:
            logger.warning(
                "SUSAR DETECTED: ae_id=%s, term=%s, subject=%s",
                ae.ae_id, ae.term, ae.subject_id,
            )

        # TODO: Persist to database
        # TODO: Publish event to Kafka (ae.reported)
        logger.info("AE reported: id=%s, is_susar=%s", ae.ae_id, ae.is_susar)
        return ae

    async def get_adverse_event(self, ae_id: UUID) -> AdverseEvent:
        """Retrieve an adverse event by ID.

        Args:
            ae_id: AE UUID.

        Returns:
            AdverseEvent instance.

        Raises:
            NotFoundError: If AE not found.
        """
        logger.debug("Fetching AE %s", ae_id)
        # TODO: Query database
        raise NotFoundError("AdverseEvent", str(ae_id))

    async def list_adverse_events(
        self,
        study_id: UUID,
        subject_id: UUID | None = None,
        serious_only: bool = False,
    ) -> list[AdverseEvent]:
        """List adverse events for a study with optional filters.

        Args:
            study_id: Parent study UUID.
            subject_id: Filter by subject.
            serious_only: Only return serious AEs.

        Returns:
            List of matching AdverseEvent instances.
        """
        logger.debug(
            "Listing AEs for study %s (subject=%s, serious_only=%s)",
            study_id, subject_id, serious_only,
        )
        # TODO: Query database with filters
        return []

    async def update_ae_outcome(
        self, ae_id: UUID, outcome: str, resolution_date: str | None = None
    ) -> AdverseEvent:
        """Update the outcome and resolution of an adverse event.

        Implements: FR-020

        Args:
            ae_id: AE UUID.
            outcome: Updated outcome.
            resolution_date: Date of resolution (ISO format).

        Returns:
            Updated AdverseEvent instance.
        """
        logger.info("Updating AE %s outcome to %s", ae_id, outcome)

        ae = await self.get_adverse_event(ae_id)
        ae.outcome = outcome
        if resolution_date:
            from datetime import date as date_type

            ae.resolution_date = date_type.fromisoformat(resolution_date)
        ae.updated_at = datetime.utcnow()

        # TODO: Persist to database
        return ae

    async def mark_reported_to_regulator(self, ae_id: UUID) -> AdverseEvent:
        """Mark an AE as having been reported to the regulatory authority.

        Args:
            ae_id: AE UUID.

        Returns:
            Updated AdverseEvent instance.
        """
        logger.info("Marking AE %s as reported to regulator", ae_id)

        ae = await self.get_adverse_event(ae_id)
        ae.reported_to_regulator = True
        ae.updated_at = datetime.utcnow()

        # TODO: Persist to database
        return ae

    @staticmethod
    def _detect_susar(ae: AdverseEvent) -> bool:
        """Apply SUSAR detection rules to an adverse event.

        A SUSAR is a Serious Unexpected Adverse Reaction.
        This implements basic detection; production would use
        MedDRA SMQ-based expectedness assessment.

        Args:
            ae: AdverseEvent to evaluate.

        Returns:
            True if the AE qualifies as a SUSAR.
        """
        if ae.seriousness != AdverseEventSeriousness.SERIOUS:
            return False
        if ae.causality and "not related" in ae.causality.lower():
            return False
        if ae.severity in {
            AdverseEventSeverity.LIFE_THREATENING,
            AdverseEventSeverity.FATAL,
        }:
            return True
        return False
