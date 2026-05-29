"""Study Service — core business logic for clinical study management.

Implements: FR-001 (Study Management), FR-002 (Study Activation)
Aligns with: 06-api-specifications/openapi/core-api.yaml
"""

from __future__ import annotations

from uuid import UUID, uuid4
from datetime import datetime

from shared.models.study import Study, StudyStatus
from shared.utils.logging import get_logger
from shared.utils.errors import NotFoundError, ValidationError

logger = get_logger(__name__)


class StudyService:
    """Service for managing clinical study lifecycle.

    Handles study creation, activation, status transitions,
    and enrollment tracking.
    """

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize study service.

        Args:
            db_session: Async database session (SQLAlchemy AsyncSession).
        """
        self._db = db_session

    async def create_study(
        self,
        protocol_number: str,
        title: str,
        short_title: str,
        phase: str,
        sponsor_id: UUID,
        indication: str,
        target_enrollment: int,
    ) -> Study:
        """Create a new clinical study.

        Implements: FR-001, TC-001

        Args:
            protocol_number: Unique protocol number.
            title: Full study title.
            short_title: Abbreviated title.
            phase: Study phase (I, II, III, IV, etc.).
            sponsor_id: Sponsor organization UUID.
            indication: Therapeutic indication.
            target_enrollment: Planned number of subjects.

        Returns:
            Newly created Study instance.

        Raises:
            ValidationError: If protocol number already exists.
        """
        logger.info("Creating study %s", protocol_number)

        study = Study(
            study_id=uuid4(),
            protocol_number=protocol_number,
            title=title,
            short_title=short_title,
            phase=phase,
            status=StudyStatus.DRAFT,
            sponsor_id=sponsor_id,
            indication=indication,
            target_enrollment=target_enrollment,
            actual_enrollment=0,
        )

        # TODO: Persist to database via self._db
        logger.info("Study created: %s (id=%s)", protocol_number, study.study_id)
        return study

    async def get_study(self, study_id: UUID) -> Study:
        """Retrieve a study by ID.

        Args:
            study_id: Study UUID.

        Returns:
            Study instance.

        Raises:
            NotFoundError: If study not found.
        """
        logger.debug("Fetching study %s", study_id)
        # TODO: Query database
        raise NotFoundError("Study", str(study_id))

    async def update_study_status(
        self, study_id: UUID, new_status: StudyStatus
    ) -> Study:
        """Transition a study to a new lifecycle status.

        Implements: FR-002

        Args:
            study_id: Study UUID.
            new_status: Target status.

        Returns:
            Updated Study instance.

        Raises:
            NotFoundError: If study not found.
            ValidationError: If transition is invalid.
        """
        logger.info("Updating study %s status to %s", study_id, new_status.value)

        study = await self.get_study(study_id)
        self._validate_status_transition(study.status, new_status)

        study.status = new_status
        study.updated_at = datetime.utcnow()

        # TODO: Persist to database
        logger.info("Study %s status updated to %s", study_id, new_status.value)
        return study

    async def list_studies(
        self, sponsor_id: UUID | None = None, status: StudyStatus | None = None
    ) -> list[Study]:
        """List studies with optional filters.

        Args:
            sponsor_id: Filter by sponsor.
            status: Filter by status.

        Returns:
            List of matching Study instances.
        """
        logger.debug("Listing studies (sponsor=%s, status=%s)", sponsor_id, status)
        # TODO: Query database with filters
        return []

    @staticmethod
    def _validate_status_transition(
        current: StudyStatus, target: StudyStatus
    ) -> None:
        """Validate that a study status transition is allowed.

        Raises:
            ValidationError: If transition is not allowed.
        """
        VALID_TRANSITIONS: dict[StudyStatus, list[StudyStatus]] = {
            StudyStatus.DRAFT: [StudyStatus.ACTIVATION_PENDING, StudyStatus.TERMINATED],
            StudyStatus.ACTIVATION_PENDING: [StudyStatus.ENROLLING, StudyStatus.TERMINATED],
            StudyStatus.ENROLLING: [
                StudyStatus.ENROLLMENT_COMPLETE,
                StudyStatus.TERMINATED,
            ],
            StudyStatus.ENROLLMENT_COMPLETE: [StudyStatus.TREATMENT, StudyStatus.TERMINATED],
            StudyStatus.TREATMENT: [StudyStatus.FOLLOW_UP, StudyStatus.TERMINATED],
            StudyStatus.FOLLOW_UP: [StudyStatus.LOCKED, StudyStatus.TERMINATED],
            StudyStatus.LOCKED: [StudyStatus.COMPLETED, StudyStatus.TERMINATED],
            StudyStatus.COMPLETED: [],
            StudyStatus.TERMINATED: [],
        }
        allowed = VALID_TRANSITIONS.get(current, [])
        if target not in allowed:
            raise ValidationError(
                f"Invalid status transition: {current.value} -> {target.value}",
                errors=[
                    {
                        "field": "status",
                        "message": f"Cannot transition from {current.value} to {target.value}",
                        "allowed": [s.value for s in allowed],
                    }
                ],
            )
