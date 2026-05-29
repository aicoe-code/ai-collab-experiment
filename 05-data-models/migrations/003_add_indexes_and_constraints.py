"""Add indexes, constraints, and missing columns to CDOS schema.

Revision ID: 003
Revises: 002
Create Date: 2026-05-29

This migration adds performance indexes, referential integrity
constraints, and missing columns to align the database schema
with the canonical Pydantic models in 08-software/shared/models/.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================
    # Add missing columns to study table
    # (Pydantic Study model has target_enrollment, actual_enrollment)
    # ============================================================

    op.add_column(
        "study",
        sa.Column("target_enrollment", sa.Integer(), nullable=True),
    )
    op.execute("UPDATE study SET target_enrollment = 0 WHERE target_enrollment IS NULL")
    op.alter_column("study", "target_enrollment", nullable=False, server_default="0")

    op.add_column(
        "study",
        sa.Column("actual_enrollment", sa.Integer(), nullable=True),
    )
    op.execute("UPDATE study SET actual_enrollment = 0 WHERE actual_enrollment IS NULL")
    op.alter_column("study", "actual_enrollment", nullable=False, server_default="0")

    # ============================================================
    # Add missing columns to subject table
    # (Pydantic Subject model has screening_date, consent_date)
    # ============================================================

    op.add_column(
        "subject",
        sa.Column("screening_date", sa.Date(), nullable=True),
    )

    op.add_column(
        "subject",
        sa.Column("consent_date", sa.Date(), nullable=True),
    )

    # ============================================================
    # Add missing columns to adverse_event table
    # (Pydantic AdverseEvent model has site_id, is_sae, is_susar,
    #  reported_to_regulator, narrative)
    # ============================================================

    op.add_column(
        "adverse_event",
        sa.Column("site_id", sa.dialects.postgresql.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_ae_site",
        "adverse_event",
        "site",
        ["site_id"],
        ["site_id"],
    )

    op.add_column(
        "adverse_event",
        sa.Column("is_sae", sa.Boolean(), nullable=True, server_default="false"),
    )
    op.execute("UPDATE adverse_event SET is_sae = false WHERE is_sae IS NULL")
    op.alter_column("adverse_event", "is_sae", nullable=False, server_default="false")

    op.add_column(
        "adverse_event",
        sa.Column("is_susar", sa.Boolean(), nullable=True, server_default="false"),
    )
    op.execute("UPDATE adverse_event SET is_susar = false WHERE is_susar IS NULL")
    op.alter_column("adverse_event", "is_susar", nullable=False, server_default="false")

    op.add_column(
        "adverse_event",
        sa.Column(
            "reported_to_regulator", sa.Boolean(), nullable=True, server_default="false"
        ),
    )
    op.execute(
        "UPDATE adverse_event SET reported_to_regulator = false WHERE reported_to_regulator IS NULL"
    )
    op.alter_column(
        "adverse_event", "reported_to_regulator", nullable=False, server_default="false"
    )

    op.add_column(
        "adverse_event",
        sa.Column("narrative", sa.String(length=5000), nullable=True),
    )

    # ============================================================
    # Add missing columns to lab_result table
    # (Pydantic LabResult model has site_id, visit_name, collection_time,
    #  status, lab_name, comments)
    # ============================================================

    op.add_column(
        "lab_result",
        sa.Column("site_id", sa.dialects.postgresql.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_lab_site",
        "lab_result",
        "site",
        ["site_id"],
        ["site_id"],
    )

    op.add_column(
        "lab_result",
        sa.Column("visit_name", sa.String(length=50), nullable=True),
    )

    op.add_column(
        "lab_result",
        sa.Column("collection_time", sa.String(length=20), nullable=True),
    )

    op.add_column(
        "lab_result",
        sa.Column("status", sa.String(length=20), nullable=True),
    )
    op.execute("UPDATE lab_result SET status = 'pending' WHERE status IS NULL")
    op.alter_column(
        "lab_result", "status", nullable=False, server_default="pending"
    )

    op.add_column(
        "lab_result",
        sa.Column("lab_name", sa.String(length=200), nullable=True),
    )

    op.add_column(
        "lab_result",
        sa.Column("comments", sa.String(length=1000), nullable=True),
    )

    # ============================================================
    # Create query table (new entity from Pydantic Query model)
    # ============================================================

    op.create_table(
        "query",
        sa.Column("query_id", sa.dialects.postgresql.UUID(), primary_key=True),
        sa.Column(
            "study_id",
            sa.dialects.postgresql.UUID(),
            sa.ForeignKey("study.study_id"),
            nullable=False,
        ),
        sa.Column(
            "subject_id",
            sa.dialects.postgresql.UUID(),
            sa.ForeignKey("subject.subject_id"),
            nullable=False,
        ),
        sa.Column(
            "site_id",
            sa.dialects.postgresql.UUID(),
            sa.ForeignKey("site.site_id"),
            nullable=False,
        ),
        sa.Column("crf_page", sa.String(length=100), nullable=False),
        sa.Column("field_name", sa.String(length=200), nullable=False),
        sa.Column("query_text", sa.String(length=2000), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column(
            "priority", sa.String(length=20), nullable=False, server_default="medium"
        ),
        sa.Column("raised_by", sa.String(length=200), nullable=False),
        sa.Column("assigned_to", sa.String(length=200), nullable=True),
        sa.Column("response", sa.String(length=2000), nullable=True),
        sa.Column("responded_by", sa.String(length=200), nullable=True),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "auto_generated", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # ============================================================
    # Composite indexes for common query patterns
    # ============================================================

    op.create_index(
        "idx_study_status_sponsor",
        "study",
        ["status", "sponsor_id"],
    )

    op.create_index(
        "idx_subject_study_status",
        "subject",
        ["study_id", "status"],
    )

    op.create_index(
        "idx_subject_site_status",
        "subject",
        ["site_id", "status"],
    )

    op.create_index(
        "idx_ae_study_severity",
        "adverse_event",
        ["study_id", "severity"],
    )

    op.create_index(
        "idx_ae_subject_onset",
        "adverse_event",
        ["subject_id", "start_date"],
    )

    op.create_index(
        "idx_lab_subject_collection",
        "lab_result",
        ["subject_id", "collection_date"],
    )

    op.create_index(
        "idx_lab_study_test_code",
        "lab_result",
        ["study_id", "test_code"],
    )

    op.create_index(
        "idx_visit_subject_number",
        "visit",
        ["subject_id", "visit_number"],
    )

    op.create_index(
        "idx_med_subject_start",
        "medication",
        ["subject_id", "start_date"],
    )

    op.create_index(
        "idx_protocol_study_effective",
        "protocol",
        ["study_id", "effective_date"],
    )

    # Query indexes
    op.create_index("idx_query_study", "query", ["study_id"])
    op.create_index("idx_query_subject", "query", ["subject_id"])
    op.create_index("idx_query_site", "query", ["site_id"])
    op.create_index("idx_query_status", "query", ["status"])
    op.create_index(
        "idx_query_study_status", "query", ["study_id", "status"]
    )

    # ============================================================
    # CHECK constraints for data integrity
    # ============================================================

    op.execute(
        "ALTER TABLE study ADD CONSTRAINT chk_study_target_enrollment "
        "CHECK (target_enrollment >= 0)"
    )

    op.execute(
        "ALTER TABLE study ADD CONSTRAINT chk_study_actual_enrollment "
        "CHECK (actual_enrollment >= 0)"
    )

    op.execute(
        "ALTER TABLE study ADD CONSTRAINT chk_study_dates "
        "CHECK (end_date IS NULL OR study_start_date IS NULL OR end_date >= study_start_date)"
    )

    op.execute(
        "ALTER TABLE adverse_event ADD CONSTRAINT chk_ae_dates "
        "CHECK (end_date IS NULL OR end_date >= start_date)"
    )

    op.execute(
        "ALTER TABLE medication ADD CONSTRAINT chk_med_dates "
        "CHECK (end_date IS NULL OR end_date >= start_date)"
    )


def downgrade() -> None:
    # Drop CHECK constraints
    op.execute("ALTER TABLE medication DROP CONSTRAINT IF EXISTS chk_med_dates")
    op.execute("ALTER TABLE adverse_event DROP CONSTRAINT IF EXISTS chk_ae_dates")
    op.execute("ALTER TABLE study DROP CONSTRAINT IF EXISTS chk_study_dates")
    op.execute(
        "ALTER TABLE study DROP CONSTRAINT IF EXISTS chk_study_actual_enrollment"
    )
    op.execute(
        "ALTER TABLE study DROP CONSTRAINT IF EXISTS chk_study_target_enrollment"
    )

    # Drop query indexes
    op.drop_index("idx_query_study_status", table_name="query")
    op.drop_index("idx_query_status", table_name="query")
    op.drop_index("idx_query_site", table_name="query")
    op.drop_index("idx_query_subject", table_name="query")
    op.drop_index("idx_query_study", table_name="query")

    # Drop composite indexes
    op.drop_index("idx_protocol_study_effective", table_name="protocol")
    op.drop_index("idx_med_subject_start", table_name="medication")
    op.drop_index("idx_visit_subject_number", table_name="visit")
    op.drop_index("idx_lab_study_test_code", table_name="lab_result")
    op.drop_index("idx_lab_subject_collection", table_name="lab_result")
    op.drop_index("idx_ae_subject_onset", table_name="adverse_event")
    op.drop_index("idx_ae_study_severity", table_name="adverse_event")
    op.drop_index("idx_subject_site_status", table_name="subject")
    op.drop_index("idx_subject_study_status", table_name="subject")
    op.drop_index("idx_study_status_sponsor", table_name="study")

    # Drop query table
    op.drop_table("query")

    # Drop lab_result additions
    op.drop_column("lab_result", "comments")
    op.drop_column("lab_result", "lab_name")
    op.drop_column("lab_result", "status")
    op.drop_column("lab_result", "collection_time")
    op.drop_column("lab_result", "visit_name")
    op.drop_constraint("fk_lab_site", "lab_result", type_="foreignkey")
    op.drop_column("lab_result", "site_id")

    # Drop adverse_event additions
    op.drop_column("adverse_event", "narrative")
    op.drop_column("adverse_event", "reported_to_regulator")
    op.drop_column("adverse_event", "is_susar")
    op.drop_column("adverse_event", "is_sae")
    op.drop_constraint("fk_ae_site", "adverse_event", type_="foreignkey")
    op.drop_column("adverse_event", "site_id")

    # Drop subject additions
    op.drop_column("subject", "consent_date")
    op.drop_column("subject", "screening_date")

    # Drop study additions
    op.drop_column("study", "actual_enrollment")
    op.drop_column("study", "target_enrollment")
