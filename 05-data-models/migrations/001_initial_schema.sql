-- CDOS Initial Schema Migration
-- Migration: 001_initial_schema
-- Author: Agent-Data
-- Description: Create core CDOS tables for canonical entities.
--              Tables are defined to match the JSON Schemas in canonical/.
--              CDISC SDTM v3.4 domain mappings noted per table.

BEGIN;

-- ============================================================
-- ENUM TYPES
-- ============================================================

CREATE TYPE study_status AS ENUM ('DRAFT', 'ACTIVE', 'ENROLLING', 'SUSPENDED', 'COMPLETED', 'TERMINATED');
CREATE TYPE study_phase AS ENUM ('Phase I', 'Phase II', 'Phase III', 'Phase IV');
CREATE TYPE subject_status AS ENUM ('SCREENING', 'ENROLLED', 'RANDOMIZED', 'ON_TREATMENT', 'COMPLETED', 'WITHDRAWN', 'SCREEN_FAILED');
CREATE TYPE sex_type AS ENUM ('M', 'F', 'U');
CREATE TYPE site_status AS ENUM ('PENDING', 'ACTIVE', 'SUSPENDED', 'CLOSED');
CREATE TYPE visit_status AS ENUM ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'MISSED', 'CANCELLED');
CREATE TYPE visit_type AS ENUM ('SCREENING', 'BASELINE', 'TREATMENT', 'FOLLOW_UP', 'END_OF_STUDY', 'UNSCHEDULED');
CREATE TYPE ae_severity AS ENUM ('MILD', 'MODERATE', 'SEVERE');
CREATE TYPE ae_seriousness AS ENUM ('NOT_SERIOUS', 'SERIOUS');
CREATE TYPE ae_causality AS ENUM ('RELATED', 'NOT_RELATED', 'POSSIBLY_RELATED', 'PROBABLY_RELATED', 'DEFINITELY_RELATED');
CREATE TYPE ae_outcome AS ENUM ('RECOVERED', 'RECOVERING', 'NOT_RECOVERED', 'FATAL', 'UNKNOWN');
CREATE TYPE ae_action AS ENUM ('NONE', 'DOSE_REDUCED', 'DRUG_INTERRUPTED', 'DRUG_WITHDRAWN', 'DOSE_NOT_CHANGED');
CREATE TYPE lab_category AS ENUM ('HEMATOLOGY', 'CHEMISTRY', 'URINALYSIS', 'IMMUNOLOGY', 'VIROLOGY', 'OTHER');
CREATE TYPE normal_flag AS ENUM ('NORMAL', 'ABNORMAL_LOW', 'ABNORMAL_HIGH', 'ABNORMAL');
CREATE TYPE med_type AS ENUM ('CONCOMITANT', 'STUDY_DRUG', 'PRIOR');
CREATE TYPE protocol_status AS ENUM ('DRAFT', 'UNDER_REVIEW', 'APPROVED', 'SUPERSEDED');
CREATE TYPE study_design AS ENUM ('RANDOMIZED_PARALLEL', 'RANDOMIZED_CROSSOVER', 'SINGLE_ARM', 'OPEN_LABEL', 'PLACEBO_CONTROLLED', 'OTHER');

-- ============================================================
-- 1. Study  (SDTM domain: DM/TS)
-- ============================================================

CREATE TABLE study (
    study_id            UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    study_name          VARCHAR(200)    NOT NULL,
    protocol_number     VARCHAR(50)     NOT NULL UNIQUE,
    short_title         VARCHAR(100),
    phase               study_phase     NOT NULL,
    status              study_status    NOT NULL DEFAULT 'DRAFT',
    sponsor_id          UUID,
    therapeutic_area    VARCHAR(100),
    indication          VARCHAR(200),
    study_start_date    DATE,
    study_end_date      DATE,
    protocol_version    VARCHAR(20),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE INDEX idx_study_status ON study(status);
CREATE INDEX idx_study_protocol_number ON study(protocol_number);
CREATE INDEX idx_study_sponsor ON study(sponsor_id);

-- ============================================================
-- 2. Site  (SDTM domain: DM — SITEID, COUNTRY)
-- ============================================================

CREATE TABLE site (
    site_id             UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    site_number         VARCHAR(20)     NOT NULL UNIQUE,
    site_name           VARCHAR(200)    NOT NULL,
    investigator_id     UUID,
    address_line1       VARCHAR(200),
    address_line2       VARCHAR(200),
    city                VARCHAR(100),
    state_province      VARCHAR(100),
    postal_code         VARCHAR(20),
    country             VARCHAR(3)      NOT NULL,
    phone               VARCHAR(30),
    email               VARCHAR(255),
    status              site_status     NOT NULL DEFAULT 'PENDING',
    activation_date     DATE,
    irb_approval_date   DATE,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE INDEX idx_site_status ON site(status);
CREATE INDEX idx_site_country ON site(country);
CREATE INDEX idx_site_investigator ON site(investigator_id);

-- ============================================================
-- 3. Subject  (SDTM domain: DM)
-- ============================================================

CREATE TABLE subject (
    subject_id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id            UUID            NOT NULL REFERENCES study(study_id),
    site_id             UUID            NOT NULL REFERENCES site(site_id),
    subject_number      VARCHAR(20),
    screening_number    VARCHAR(20),
    status              subject_status  NOT NULL DEFAULT 'SCREENING',
    enrollment_date     DATE,
    date_of_birth       DATE,
    sex                 sex_type,
    race                VARCHAR(100),
    ethnicity           VARCHAR(100),
    treatment_arm       VARCHAR(50),
    randomization_date  DATE,
    withdrawal_date     DATE,
    withdrawal_reason   VARCHAR(200),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE INDEX idx_subject_study ON subject(study_id);
CREATE INDEX idx_subject_site ON subject(site_id);
CREATE INDEX idx_subject_status ON subject(status);
CREATE UNIQUE INDEX idx_subject_study_number ON subject(study_id, subject_number);

-- ============================================================
-- 4. Protocol  (SDTM domain: TS, TI)
-- ============================================================

CREATE TABLE protocol (
    protocol_id         UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id            UUID            NOT NULL REFERENCES study(study_id),
    version             VARCHAR(20)     NOT NULL,
    effective_date      DATE,
    status              protocol_status NOT NULL DEFAULT 'DRAFT',
    title               VARCHAR(500),
    objective_primary   TEXT,
    objective_secondary TEXT[],
    study_design        study_design,
    is_blinded          BOOLEAN,
    blinding_procedure  VARCHAR(200),
    number_of_arms      INTEGER         CHECK (number_of_arms >= 1),
    inclusion_criteria  TEXT[],
    exclusion_criteria  TEXT[],
    endpoints_primary   TEXT[],
    endpoints_secondary TEXT[],
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE INDEX idx_protocol_study ON protocol(study_id);
CREATE UNIQUE INDEX idx_protocol_study_version ON protocol(study_id, version);

-- ============================================================
-- 5. Visit  (SDTM domain: SV)
-- ============================================================

CREATE TABLE visit (
    visit_id                UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id                UUID            NOT NULL REFERENCES study(study_id),
    subject_id              UUID            NOT NULL REFERENCES subject(subject_id),
    site_id                 UUID            REFERENCES site(site_id),
    visit_name              VARCHAR(50)     NOT NULL,
    visit_number            INTEGER         NOT NULL CHECK (visit_number >= 1),
    visit_scheduled_date    DATE,
    visit_actual_date       DATE,
    visit_window_start      DATE,
    visit_window_end        DATE,
    status                  visit_status    NOT NULL DEFAULT 'SCHEDULED',
    visit_type              visit_type,
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE INDEX idx_visit_study ON visit(study_id);
CREATE INDEX idx_visit_subject ON visit(subject_id);
CREATE INDEX idx_visit_site ON visit(site_id);
CREATE INDEX idx_visit_status ON visit(status);
CREATE INDEX idx_visit_scheduled ON visit(visit_scheduled_date);

-- ============================================================
-- 6. AdverseEvent  (SDTM domain: AE)
-- ============================================================

CREATE TABLE adverse_event (
    ae_id               UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id            UUID            NOT NULL REFERENCES study(study_id),
    subject_id          UUID            NOT NULL REFERENCES subject(subject_id),
    visit_id            UUID            REFERENCES visit(visit_id),
    ae_sequence         INTEGER         CHECK (ae_sequence >= 1),
    term                VARCHAR(200)    NOT NULL,
    meddra_code         VARCHAR(20),
    meddra_llt          VARCHAR(100),
    meddra_pt           VARCHAR(100),
    meddra_soc          VARCHAR(100),
    severity            ae_severity     NOT NULL,
    seriousness         ae_seriousness,
    causality           ae_causality,
    outcome             ae_outcome,
    action_taken        ae_action,
    start_date          DATE            NOT NULL,
    end_date            DATE,
    is_ongoing          BOOLEAN,
    reported_by         VARCHAR(100),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE INDEX idx_ae_study ON adverse_event(study_id);
CREATE INDEX idx_ae_subject ON adverse_event(subject_id);
CREATE INDEX idx_ae_visit ON adverse_event(visit_id);
CREATE INDEX idx_ae_severity ON adverse_event(severity);
CREATE INDEX idx_ae_meddra_soc ON adverse_event(meddra_soc);
CREATE INDEX idx_ae_start_date ON adverse_event(start_date);

-- ============================================================
-- 7. LabResult  (SDTM domain: LB)
-- ============================================================

CREATE TABLE lab_result (
    lab_id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id                UUID            NOT NULL REFERENCES study(study_id),
    subject_id              UUID            NOT NULL REFERENCES subject(subject_id),
    visit_id                UUID            NOT NULL REFERENCES visit(visit_id),
    lab_sequence            INTEGER         CHECK (lab_sequence >= 1),
    test_name               VARCHAR(100)    NOT NULL,
    test_code               VARCHAR(20)     NOT NULL,
    category                lab_category,
    result                  VARCHAR(200)    NOT NULL,
    result_numeric          DECIMAL,
    unit                    VARCHAR(20),
    reference_range_low     DECIMAL,
    reference_range_high    DECIMAL,
    normal_flag             normal_flag,
    specimen_type           VARCHAR(50),
    collection_date         DATE,
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE INDEX idx_lab_study ON lab_result(study_id);
CREATE INDEX idx_lab_subject ON lab_result(subject_id);
CREATE INDEX idx_lab_visit ON lab_result(visit_id);
CREATE INDEX idx_lab_test_code ON lab_result(test_code);
CREATE INDEX idx_lab_category ON lab_result(category);
CREATE INDEX idx_lab_normal_flag ON lab_result(normal_flag);

-- ============================================================
-- 8. Medication  (SDTM domain: CM / EX)
-- ============================================================

CREATE TABLE medication (
    med_id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    study_id            UUID            NOT NULL REFERENCES study(study_id),
    subject_id          UUID            NOT NULL REFERENCES subject(subject_id),
    visit_id            UUID            REFERENCES visit(visit_id),
    med_sequence        INTEGER         CHECK (med_sequence >= 1),
    medication_name     VARCHAR(200)    NOT NULL,
    who_drug_code       VARCHAR(20),
    medication_type     med_type,
    dose                VARCHAR(50),
    dose_unit           VARCHAR(20),
    route               VARCHAR(50),
    frequency           VARCHAR(50),
    indication          VARCHAR(200),
    start_date          DATE            NOT NULL,
    end_date            DATE,
    is_ongoing          BOOLEAN,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE INDEX idx_med_study ON medication(study_id);
CREATE INDEX idx_med_subject ON medication(subject_id);
CREATE INDEX idx_med_visit ON medication(visit_id);
CREATE INDEX idx_med_type ON medication(medication_type);
CREATE INDEX idx_med_start_date ON medication(start_date);

-- ============================================================
-- Junction: Study-Site (many-to-many)
-- ============================================================

CREATE TABLE study_site (
    study_id        UUID    NOT NULL REFERENCES study(study_id),
    site_id         UUID    NOT NULL REFERENCES site(site_id),
    enrollment_target INTEGER,
    enrolled_count  INTEGER DEFAULT 0,
    activated_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (study_id, site_id)
);

CREATE INDEX idx_study_site_site ON study_site(site_id);

-- ============================================================
-- Audit trigger for updated_at
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_study_updated_at BEFORE UPDATE ON study FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_site_updated_at BEFORE UPDATE ON site FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_subject_updated_at BEFORE UPDATE ON subject FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_protocol_updated_at BEFORE UPDATE ON protocol FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_visit_updated_at BEFORE UPDATE ON visit FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_ae_updated_at BEFORE UPDATE ON adverse_event FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_lab_updated_at BEFORE UPDATE ON lab_result FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER trg_med_updated_at BEFORE UPDATE ON medication FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;
