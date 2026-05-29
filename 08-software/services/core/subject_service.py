"""Subject Service — core business logic for subject enrollment and management.

Implements: FR-015 (Subject Enrollment), FR-016 (Subject Discontinuation)
Aligns with: 06-api-specifications/openapi/core-api.yaml
"""

from __future__ import annotations

from uuid import UUID, uuid4
from datetime import datetime

from shared.models.subject import Subject, SubjectStatus
from shared.utils.logging import get_logger
from shared.utils.errors import NotFoundError, ValidationError

logger = get_logger(__name__)


class SubjectService:
    """Service for managing study subject enrollment and lifecycle.

    Handles screening, enrollment, discontinuation, and status tracking.
    """

    def __init__(self, db_session: object | None = None) -> None:
        """Initialize subject service.

        Args:
            db_session: Async database session (SQLAlchemy AsyncSession).
        """
        self._db = db_session

    async def screen_subject(
        self,
        study_id: UUID,
        site_id: UUID,
        subject_number: str,
    ) -> Subject:
        """Screen a new subject for a study.

        Implements: FR-015, TC-042

        Args:
            study_id: Parent study UUID.
            site_id: Enrolling site UUID.
            subject_number: Subject number within the study.

        Returns:
            Newly created Subject in SCREENING status.

        Raises:
            ValidationError: If subject number already exists for study.
        """
        logger.info(
            "Screening subject %s for study %s at site %s",
            subject_number, study_id, site_id,
        )

        subject = Subject(
            subject_id=uuid4(),
            study_id=study_id,
            site_id=site_id,
            subject_number=subject_number,
            status=SubjectStatus.SCREENING,
        )

        # TODO: Persist to database
        logger.info("Subject screened: %s (id=%s)", subject_number, subject.subject_id)
        return subject

    async def enroll_subject(self, subject_id: UUID) -> Subject:
        """Enroll a screened subject into the study.

        Implements: FR-015, TC-042

        Args:
            subject_id: Subject UUID.

        Returns:
            Updated Subject in ENROLLED status.

        Raises:
            NotFoundError: If subject not found.
            ValidationError: If subject is not in SCREENING status.
        """
        from datetime import date

        logger.info("Enrolling subject %s", subject_id)

        subject = await self.get_subject(subject_id)
        if subject.status != SubjectStatus.SCREENING:
            raise ValidationError(
                f"Subject must be in SCREENING status to enroll, current: {subject.status.value}",
                errors=[{"field": "status", "message": "Subject not in screening status"}],
            )

        subject.status = SubjectStatus.ENROLLED
        subject.enrollment_date = date.today()
        subject.updated_at = datetime.utcnow()

        # TODO: Persist to database
        logger.info("Subject %s enrolled", subject_id)
        return subject

    async def discontinue_subject(
        self, subject_id: UUID, reason: str
    ) -> Subject:
        """Discontinue a subject from the study.

        Implements: FR-016

        Args:
            subject_id: Subject UUID.
            reason: Reason for discontinuation.

        Returns:
            Updated Subject in DISCONTINUED status.
        """
        logger.info("Discontinuing subject %s: %s", subject_id, reason)

        subject = await self.get_subject(subject_id)
        subject.status = SubjectStatus.DISCONTINUED
        subject.discontinuation_reason = reason
        subject.updated_at = datetime.utcnow()

        # TODO: Persist to database
        logger.info("Subject %s discontinued", subject_id)
        return subject

    async def get_subject(self, subject_id: UUID) -> Subject:
        """Retrieve a subject by ID.

        Args:
            subject_id: Subject UUID.

        Returns:
            Subject instance.

        Raises:
            NotFoundError: If subject not found.
        """
        logger.debug("Fetching subject %s", subject_id)
        # TODO: Query database
        raise NotFoundError("Subject", str(subject_id))

    async def list_subjects(
        self,
        study_id: UUID,
        site_id: UUID | None = None,
        status: SubjectStatus | None = None,
    ) -> list[Subject]:
        """List subjects for a study with optional filters.

        Args:
            study_id: Parent study UUID.
            site_id: Filter by site.
            status: Filter by status.

        Returns:
            List of matching Subject instances.
        """
        logger.debug(
            "Listing subjects for study %s (site=%s, status=%s)",
            study_id, site_id, status,
        )
        # TODO: Query database with filters
        return []
