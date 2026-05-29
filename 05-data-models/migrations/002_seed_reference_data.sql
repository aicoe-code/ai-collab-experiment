-- CDOS Seed Reference Data Migration
-- Migration: 002_seed_reference_data
-- Author: Agent-Data
-- Description: Insert controlled terminology reference data
--              sourced from CDISC CT, MedDRA, WHO Drug, ISO 3166-1, UCUM.

BEGIN;

-- ============================================================
-- CDISC Controlled Terminology (SDTM CT)
-- ============================================================

CREATE TABLE cdisc_controlled_terminology (
    id              SERIAL      PRIMARY KEY,
    codelist_code   VARCHAR(20) NOT NULL,
    codelist_name   VARCHAR(100) NOT NULL,
    term_code       VARCHAR(20) NOT NULL,
    term_value      VARCHAR(200) NOT NULL,
    submission_value VARCHAR(100) NOT NULL,
    preferred_term  VARCHAR(200),
    definition      TEXT,
    UNIQUE(codelist_code, term_code)
);

-- Sex (C66731)
INSERT INTO cdisc_controlled_terminology (codelist_code, codelist_name, term_code, term_value, submission_value, preferred_term, definition) VALUES
('C66731', 'Sex', 'C20197', 'Male', 'M', 'Male', 'A biological sex designation of male.'),
('C66731', 'Sex', 'C16576', 'Female', 'F', 'Female', 'A biological sex designation of female.'),
('C66731', 'Sex', 'C17998', 'Unknown', 'U', 'Unknown', 'The sex is not known.');

-- Race (C74457)
INSERT INTO cdisc_controlled_terminology (codelist_code, codelist_name, term_code, term_value, submission_value, preferred_term, definition) VALUES
('C74457', 'Race', 'C41260', 'American Indian or Alaska Native', 'AMERICAN INDIAN OR ALASKA NATIVE', 'American Indian or Alaska Native', 'A person having origins in any of the original peoples of North and South America.'),
('C74457', 'Race', 'C41259', 'Asian', 'ASIAN', 'Asian', 'A person having origins in any of the original peoples of the Far East, Southeast Asia, or the Indian subcontinent.'),
('C74457', 'Race', 'C16352', 'Black or African American', 'BLACK OR AFRICAN AMERICAN', 'Black or African American', 'A person having origins in any of the black racial groups of Africa.'),
('C74457', 'Race', 'C41219', 'Native Hawaiian or Other Pacific Islander', 'NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER', 'Native Hawaiian or Other Pacific Islander', 'A person having origins in any of the original peoples of Hawaii, Guam, Samoa, or other Pacific Islands.'),
('C74457', 'Race', 'C85494', 'White', 'WHITE', 'White', 'A person having origins in any of the original peoples of Europe, the Middle East, or North Africa.'),
('C74457', 'Race', 'C43234', 'Not Reported', 'NOT REPORTED', 'Not Reported', 'Race was not collected.'),
('C74457', 'Race', 'C116962', 'Unknown', 'UNKNOWN', 'Unknown', 'Race is not known.');

-- Adverse Event Severity (C66769)
INSERT INTO cdisc_controlled_terminology (codelist_code, codelist_name, term_code, term_value, submission_value, preferred_term, definition) VALUES
('C66769', 'Severity/Intensity Scale for AE', 'C70689', 'Mild', 'MILD', 'Mild', 'An AE that is usually transient and requires no special treatment.'),
('C70689', 'Severity/Intensity Scale for AE', 'C70690', 'Moderate', 'MODERATE', 'Moderate', 'An AE that is sufficiently discomforting to interfere with daily activity.'),
('C70689', 'Severity/Intensity Scale for AE', 'C70691', 'Severe', 'SEVERE', 'Severe', 'An AE that prevents normal daily activity.');

-- Serious Adverse Event (C66770)
INSERT INTO cdisc_controlled_terminology (codelist_code, codelist_name, term_code, term_value, submission_value, preferred_term, definition) VALUES
('C66770', 'Serious Event', 'C49487', 'Yes', 'Y', 'Yes', 'The AE meets criteria for a serious adverse event.'),
('C66770', 'Serious Event', 'C49488', 'No', 'N', 'No', 'The AE does not meet criteria for a serious adverse event.');

-- AE Causality (C66768)
INSERT INTO cdisc_controlled_terminology (codelist_code, codelist_name, term_code, term_value, submission_value, preferred_term, definition) VALUES
('C66768', 'Causality', 'C48660', 'Not Related', 'NOT RELATED', 'Not Related', 'The event is not related to study drug.'),
('C66768', 'Causality', 'C53263', 'Possibly Related', 'POSSIBLY RELATED', 'Possibly Related', 'The event may be related to study drug.'),
('C66768', 'Causality', 'C53264', 'Probably Related', 'PROBABLY RELATED', 'Probably Related', 'The event is probably related to study drug.'),
('C66768', 'Causality', 'C53265', 'Definitely Related', 'DEFINITELY RELATED', 'Definitely Related', 'The event is definitely related to study drug.'),
('C66768', 'Causality', 'C48661', 'Related', 'RELATED', 'Related', 'The event is related to study drug.');

-- AE Outcome (C66767)
INSERT INTO cdisc_controlled_terminology (codelist_code, codelist_name, term_code, term_value, submission_value, preferred_term, definition) VALUES
('C66767', 'Outcome of Event', 'C49483', 'Recovered', 'RECOVERED', 'Recovered', 'The event has resolved.'),
('C66767', 'Outcome of Event', 'C49486', 'Recovering/Resolving', 'RECOVERING', 'Recovering', 'The event is resolving.'),
('C66767', 'Outcome of Event', 'C49484', 'Not Recovered/Not Resolved', 'NOT RECOVERED', 'Not Recovered', 'The event has not resolved.'),
('C66767', 'Outcome of Event', 'C48648', 'Fatal', 'FATAL', 'Fatal', 'The event resulted in death.'),
('C66767', 'Outcome of Event', 'C49485', 'Unknown', 'UNKNOWN', 'Unknown', 'The outcome is not known.');

-- Action Taken with Study Drug (C66766)
INSERT INTO cdisc_controlled_terminology (codelist_code, codelist_name, term_code, term_value, submission_value, preferred_term, definition) VALUES
('C66766', 'Action Taken with Study Treatment', 'C48653', 'None', 'NONE', 'None', 'No action taken.'),
('C66766', 'Action Taken with Study Treatment', 'C49493', 'Dose Reduced', 'DOSE REDUCED', 'Dose Reduced', 'The dose of study drug was reduced.'),
('C66766', 'Action Taken with Study Treatment', 'C49494', 'Drug Interrupted', 'DRUG INTERRUPTED', 'Drug Interrupted', 'Study drug was temporarily interrupted.'),
('C66766', 'Action Taken with Study Treatment', 'C49495', 'Drug Withdrawn', 'DRUG WITHDRAWN', 'Drug Withdrawn', 'Study drug was permanently withdrawn.'),
('C66766', 'Action Taken with Study Treatment', 'C49502', 'Dose Not Changed', 'DOSE NOT CHANGED', 'Dose Not Changed', 'The dose of study drug was not changed.');

-- Lab Normal Flag (C78734)
INSERT INTO cdisc_controlled_terminology (codelist_code, codelist_name, term_code, term_value, submission_value, preferred_term, definition) VALUES
('C78734', 'Normal Abnormal', 'C78735', 'NORMAL', 'NORMAL', 'Normal', 'Within normal range.'),
('C78734', 'Normal Abnormal', 'C78736', 'ABNORMAL', 'ABNORMAL', 'Abnormal', 'Outside normal range.'),
('C78734', 'Normal Abnormal', 'C78737', 'ABNORMAL LOW', 'ABNORMAL LOW', 'Abnormal Low', 'Below the normal range.'),
('C78734', 'Normal Abnormal', 'C78738', 'ABNORMAL HIGH', 'ABNORMAL HIGH', 'Abnormal High', 'Above the normal range.');

-- ============================================================
-- MedDRA System Organ Class (SOC) Reference — Top-Level
-- ============================================================

CREATE TABLE meddra_soc_reference (
    soc_code    VARCHAR(10) PRIMARY KEY,
    soc_name    VARCHAR(200) NOT NULL
);

INSERT INTO meddra_soc_reference (soc_code, soc_name) VALUES
('10000001', 'Administration site conditions'),
('10000005', 'Blood and lymphatic system disorders'),
('10000016', 'Cardiac disorders'),
('10000019', 'Congenital, familial and genetic disorders'),
('10000027', 'Ear and labyrinth disorders'),
('10000029', 'Endocrine disorders'),
('10000032', 'Eye disorders'),
('10000038', 'Gastrointestinal disorders'),
('10000045', 'General disorders and administration site conditions'),
('10000053', 'Hepatobiliary disorders'),
('10000055', 'Immune system disorders'),
('10000059', 'Infections and infestations'),
('10000071', 'Injury, poisoning and procedural complications'),
('10000078', 'Investigations'),
('10000080', 'Metabolism and nutrition disorders'),
('10000097', 'Musculoskeletal and connective tissue disorders'),
('10000103', 'Neoplasms benign, malignant and unspecified'),
('10000109', 'Nervous system disorders'),
('10000119', 'Pregnancy, puerperium and perinatal conditions'),
('10000122', 'Psychiatric disorders'),
('10000130', 'Renal and urinary disorders'),
('10000133', 'Reproductive system and breast disorders'),
('10000139', 'Respiratory, thoracic and mediastinal disorders'),
('10000148', 'Skin and subcutaneous tissue disorders'),
('10000151', 'Social circumstances'),
('10000154', 'Surgical and medical procedures'),
('10000162', 'Vascular disorders');

-- ============================================================
-- WHO Drug Dictionary — Sample Anatomical Main Group Codes
-- ============================================================

CREATE TABLE who_drug_atc_reference (
    atc_code    VARCHAR(10) PRIMARY KEY,
    atc_name    VARCHAR(300) NOT NULL,
    level       INTEGER      NOT NULL
);

INSERT INTO who_drug_atc_reference (atc_code, atc_name, level) VALUES
('A', 'ALIMENTARY TRACT AND METABOLISM', 1),
('B', 'BLOOD AND BLOOD FORMING ORGANS', 1),
('C', 'CARDIOVASCULAR SYSTEM', 1),
('D', 'DERMATOLOGICALS', 1),
('G', 'GENITO-URINARY SYSTEM AND SEX HORMONES', 1),
('H', 'SYSTEMIC HORMONAL PREPARATIONS', 1),
('J', 'ANTIINFECTIVES FOR SYSTEMIC USE', 1),
('L', 'ANTINEOPLASTIC AND IMMUNOMODULATING AGENTS', 1),
('M', 'MUSCULO-SKELETAL SYSTEM', 1),
('N', 'NERVOUS SYSTEM', 1),
('P', 'ANTIPARASITIC PRODUCTS', 1),
('R', 'RESPIRATORY SYSTEM', 1),
('S', 'SENSORY ORGANS', 1),
('V', 'VARIOUS', 1);

-- ============================================================
-- ISO 3166-1 Country Codes (subset)
-- ============================================================

CREATE TABLE iso_country_code (
    alpha2  VARCHAR(2)  PRIMARY KEY,
    alpha3  VARCHAR(3)  NOT NULL,
    name    VARCHAR(100) NOT NULL
);

INSERT INTO iso_country_code (alpha2, alpha3, name) VALUES
('US', 'USA', 'United States of America'),
('CA', 'CAN', 'Canada'),
('GB', 'GBR', 'United Kingdom'),
('DE', 'DEU', 'Germany'),
('FR', 'FRA', 'France'),
('JP', 'JPN', 'Japan'),
('CN', 'CHN', 'China'),
('IN', 'IND', 'India'),
('AU', 'AUS', 'Australia'),
('BR', 'BRA', 'Brazil'),
('MX', 'MEX', 'Mexico'),
('ES', 'ESP', 'Spain'),
('IT', 'ITA', 'Italy'),
('NL', 'NLD', 'Netherlands'),
('KR', 'KOR', 'Korea, Republic of'),
('SE', 'SWE', 'Sweden'),
('CH', 'CHE', 'Switzerland'),
('PL', 'POL', 'Poland'),
('AR', 'ARG', 'Argentina'),
('ZA', 'ZAF', 'South Africa'),
('RU', 'RUS', 'Russian Federation'),
('EG', 'EGY', 'Egypt'),
('TH', 'THA', 'Thailand'),
('TR', 'TUR', 'Turkey'),
('CO', 'COL', 'Colombia');

-- ============================================================
-- UCUM Units (subset for lab results)
-- ============================================================

CREATE TABLE ucum_unit (
    ucum_code   VARCHAR(20) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    category    VARCHAR(50)
);

INSERT INTO ucum_unit (ucum_code, name, category) VALUES
('g/dL', 'grams per deciliter', 'Concentration'),
('g/L', 'grams per liter', 'Concentration'),
('mg/dL', 'milligrams per deciliter', 'Concentration'),
('mg/L', 'milligrams per liter', 'Concentration'),
('mmol/L', 'millimoles per liter', 'Concentration'),
('umol/L', 'micromoles per liter', 'Concentration'),
('U/L', 'units per liter', 'Enzyme Activity'),
('10*3/uL', 'thousands per microliter', 'Hematology'),
('10*6/uL', 'millions per microliter', 'Hematology'),
('%', 'percent', 'Percentage'),
('fL', 'femtoliters', 'Hematology'),
('pg', 'picograms', 'Mass'),
('mm/h', 'millimeters per hour', 'Rate'),
('mEq/L', 'milliequivalents per liter', 'Concentration'),
('ng/mL', 'nanograms per milliliter', 'Concentration'),
('pg/mL', 'picograms per milliliter', 'Concentration'),
('IU/L', 'international units per liter', 'Enzyme Activity'),
('mL/min', 'milliliters per minute', 'Flow Rate');

-- ============================================================
-- CDISC Trial Summary Parameters (subset)
-- ============================================================

CREATE TABLE cdisc_ts_parameters (
    parameter_code  VARCHAR(20) PRIMARY KEY,
    parameter_name  VARCHAR(100) NOT NULL,
    data_type       VARCHAR(20)  NOT NULL,
    description     TEXT
);

INSERT INTO cdisc_ts_parameters (parameter_code, parameter_name, data_type, description) VALUES
('TITLE', 'Study Title', 'CHAR', 'Full title of the clinical study'),
('PROTOCOL', 'Protocol Identifier', 'CHAR', 'Protocol identification number'),
('PHASE', 'Study Phase', 'CHAR', 'Phase of the clinical trial'),
('STDYDES', 'Study Design', 'CHAR', 'Description of the study design'),
('SPONSID', 'Sponsor Identifier', 'CHAR', 'Unique identifier for the sponsor'),
('INDIC', 'Indication', 'CHAR', 'Disease or condition being studied'),
('SSTDTC', 'Study Start Date', 'DATE', 'Date of first subject first visit'),
('SENDTC', 'Study End Date', 'DATE', 'Planned or actual study end date'),
('OBJPRIN', 'Primary Objective', 'CHAR', 'Primary study objective'),
('OBJSEC', 'Secondary Objective', 'CHAR', 'Secondary study objectives'),
('ARMSN', 'Number of Arms', 'NUM', 'Number of study arms'),
('BINDSC', 'Blinding Schema', 'CHAR', 'Type of blinding used');

COMMIT;
