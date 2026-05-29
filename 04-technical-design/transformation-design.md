# CDOS — Transformation Design

## 1. Overview

This document defines the transformation pipeline architecture for CDOS. Clinical data flows through four distinct stages: Raw Ingest → Canonical Normalization → CDISC Mapping → Submission Packaging. This design satisfies:
- **04-C**: Pipeline architecture (raw→canonical→CDISC→submission), transform engine design

---

## 2. Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TRANSFORMATION PIPELINE                                   │
│                                                                              │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ STAGE 1  │    │ STAGE 2      │    │ STAGE 3      │    │ STAGE 4      │  │
│  │ Raw      │───▶│ Canonical    │───▶│ CDISC        │───▶│ Submission   │  │
│  │ Ingest   │    │ Normalize    │    │ Mapping      │    │ Packaging    │  │
│  └──────────┘    └──────────────┘    └──────────────┘    └──────────────┘  │
│       │                │                    │                    │           │
│       ▼                ▼                    ▼                    ▼           │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │RawPayload│    │CanonicalModel│    │SDTM/ADaM     │    │Submission    │  │
│  │Table     │    │Tables        │    │Tables        │    │Package       │  │
│  │(PostgreSQL)│  │(PostgreSQL)  │    │(PostgreSQL)  │    │(S3/MinIO)    │  │
│  └──────────┘    └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                                              │
│  Events:         Events:              Events:              Events:           │
│  raw.ingested    canonical.created     sdtm.mapped          submission.ready │
│  raw.failed      canonical.updated     adam.mapped           submission.sent │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Stage 1: Raw Ingest

### 3.1 Purpose
Capture source system data exactly as received, preserving original format and metadata for auditability (21 CFR Part 11).

### 3.2 Design

```
Source System → Adapter.fetch() → RawIngestTransform → raw_payloads table
                                        │
                                        ▼
                                  Emit: raw.ingested event
```

### 3.3 RawIngestTransform

```python
class RawIngestTransform(BaseTransform):
    """
    Stage 1: Store raw payload with metadata.
    No transformation — preserves original data for audit trail.
    """

    def transform(self, input: RawIngestInput) -> RawPayload:
        """
        1. Generate unique payload_id (UUID)
        2. Store raw data as-is (JSONB or BLOB)
        3. Attach metadata: source_system, adapter_id, ingested_at, checksum
        4. Emit raw.ingested event to Kafka
        5. Return RawPayload entity
        """
        ...

    def validate(self, input: RawIngestInput) -> ValidationResult:
        """
        - Source system is known
        - Payload is non-empty
        - Checksum matches (data integrity)
        """
        ...
```

### 3.4 Raw Payload Storage

| Column | Type | Description |
|--------|------|-------------|
| payload_id | UUID | Primary key |
| source_system | VARCHAR(50) | EDC, CTMS, LIMS, etc. |
| adapter_class | VARCHAR(100) | Concrete adapter used |
| raw_data | JSONB | Original payload |
| checksum | VARCHAR(64) | SHA-256 of raw_data |
| ingested_at | TIMESTAMP | Ingestion timestamp |
| study_id | UUID | Associated study (if determinable) |
| status | ENUM | RECEIVED, VALIDATED, FAILED |

---

## 4. Stage 2: Canonical Normalization

### 4.1 Purpose
Map vendor-specific data structures to CDOS canonical entities (Study, Subject, AdverseEvent, LabResult, etc.).

### 4.2 Design

```
RawPayload → CanonicalNormalizeTransform → Canonical Entity Tables
                      │
                      ▼
               Emit: canonical.created / canonical.updated events
```

### 4.3 Mapping Strategy

Each source system requires a concrete transform:

| Source System | Transform Class | Target Entities |
|--------------|----------------|-----------------|
| EDC (Rave) | EDCRaveCanonicalTransform | Subject, CRFPage, AdverseEvent, LabResult, Medication |
| EDC (InForm) | EDCInFormCanonicalTransform | Subject, CRFPage, AdverseEvent, LabResult, Medication |
| CTMS | CTMSCanonicalTransform | Study, Site, Investigator, Visit |
| LIMS | LIMSCanonicalTransform | LabResult, Sample |
| Safety | SafetyCanonicalTransform | AdverseEvent |
| IWRS | IWRSCanonicalTransform | Subject (randomization), Dose |
| eCOA | eCOACanonicalTransform | Subject (outcomes) |
| Imaging | ImagingCanonicalTransform | Subject (imaging results) |
| Wearables | WearablesCanonicalTransform | Subject (sensor data) |

### 4.4 CanonicalNormalizeTransform

```python
class CanonicalNormalizeTransform(BaseTransform):
    """
    Stage 2: Map vendor-specific data to canonical model.
    Abstract base — each source has a concrete implementation.
    """

    @abstractmethod
    def transform(self, raw_payload: RawPayload) -> list[CanonicalEntity]:
        """
        1. Parse raw_data based on source_system format
        2. Map vendor fields to canonical entity attributes
        3. Resolve foreign keys (e.g., subject_id from subject_number)
        4. Apply business rules (e.g., status derivation)
        5. Upsert canonical entities
        6. Emit canonical.created or canonical.updated events
        7. Return list of created/updated entities
        """
        ...

    @abstractmethod
    def validate(self, raw_payload: RawPayload) -> ValidationResult:
        """
        - Required fields present
        - Data types correct
        - Referential integrity (subject exists for AE)
        - Business rules (e.g., onset_date <= resolution_date)
        """
        ...
```

### 4.5 Field Mapping Examples

**EDC Rave → Subject:**

| Rave Field | Canonical Field | Transform Rule |
|-----------|----------------|----------------|
| Subject.ETSUBID | subject_number | Direct copy |
| Subject.SITEID | site_id | Lookup site_id by site_number |
| Subject.STUDYID | study_id | Lookup study_id by protocol_number |
| Subject.ENRLDAT | enrolled_date | Parse ISO 8601 date |
| Subject.SEX | demographics.sex | Map Rave code → CDISC code (M/F) |
| Subject.AGE | demographics.age | Direct copy |

**EDC Rave → AdverseEvent:**

| Rave Field | Canonical Field | Transform Rule |
|-----------|----------------|----------------|
| AE.AETERM | term | Direct copy |
| AE.AESEV | severity | Map: 1→MILD, 2→MODERATE, 3→SEVERE |
| AE.AESER | seriousness | Map: Y→SERIOUS, N→NOT_SERIOUS |
| AE.AESTDAT | onset_date | Parse ISO 8601 date |
| AE.AEENDAT | resolution_date | Parse ISO 8601 date (nullable) |

---

## 5. Stage 3: CDISC Mapping

### 5.1 Purpose
Transform canonical entities to CDISC standards (SDTM v3.4, ADaM v2.1) for regulatory submission.

### 5.2 Design

```
Canonical Entities → SdtmMappingTransform → SDTM Domains (DM, AE, LB, EX, CM, ...)
Canonical Entities → AdamMappingTransform  → ADaM Datasets (ADSL, ADAE, ADLB, ...)
```

### 5.3 SDTM Domain Mapping

| Canonical Entity | SDTM Domain | Mapping Type |
|-----------------|-------------|--------------|
| Subject + Study | DM (Demographics) | 1:1 with enrichment |
| AdverseEvent | AE | 1:1 direct |
| LabResult | LB | 1:1 direct |
| Dose | EX | 1:1 direct |
| Medication | CM | 1:1 direct |
| Visit | SV | 1:1 direct |

### 5.4 SdtmMappingTransform

```python
class SdtmMappingTransform(BaseTransform):
    """
    Stage 3a: Map canonical model to SDTM domains.
    Implements CDISC SDTM v3.4 mapping rules.
    """

    def transform(self, canonical_entities: list[CanonicalEntity], 
                  study_id: UUID) -> SDTMDataset:
        """
        For each entity type:
        1. Load canonical entities for study
        2. Apply SDTM variable mapping (see CDISC IG)
        3. Derive computed variables:
           - STUDYID from Study.protocol_number
           - USUBJID = STUDYID-SUBJID
           - DOMAIN from entity type
           - Sequence numbers (AESEQ, LBSEQ, etc.)
        4. Apply controlled terminology (MedDRA, WHO Drug, CDISC CT)
        5. Write SDTM dataset (SAS XPT or CSV)
        6. Generate Define-XML metadata
        7. Emit sdtm.mapped event
        """
        ...

    def validate(self, dataset: SDTMDataset) -> ValidationResult:
        """
        - All required SDTM variables present
        - Controlled terms valid
        - No duplicate records per key
        - Referential integrity across domains
        """
        ...
```

### 5.5 ADaM Mapping

```python
class AdamMappingTransform(BaseTransform):
    """
    Stage 3b: Map canonical model to ADaM datasets.
    Implements CDISC ADaM v2.1.
    """

    def transform(self, sdtm_datasets: dict[str, SDTMDataset],
                  analysis_metadata: dict) -> AdamDataset:
        """
        1. Load SDTM datasets (DM, AE, LB, EX, etc.)
        2. Create analysis datasets:
           - ADSL: Subject-level analysis (from DM + derived flags)
           - ADAE: Adverse event analysis (from AE + severity flags)
           - ADLB: Lab analysis (from LB + shift flags + ANRIND)
        3. Derive analysis variables:
           - TRT01P, TRT01A (planned/actual treatment)
           - ASEQ, APERIOD, AWEEK
           - Shift flags (BNRIND, ANRIND)
        4. Apply ADaM metadata (PARAMCD, AVAL, AVALC)
        5. Generate Define-XML for ADaM
        6. Emit adam.mapped event
        """
        ...
```

---

## 6. Stage 4: Submission Packaging

### 6.1 Purpose
Package CDISC datasets, Define-XML, and supporting documents into a regulatory submission package.

### 6.2 Design

```
SDTM + ADaM datasets → SubmissionPackageTransform → Submission Package (S3)
                                                              │
                                                              ▼
                                                     Emit: submission.ready event
                                                              │
                                                              ▼
                                                     RegSubmit Adapter → Agency
```

### 6.3 SubmissionPackageTransform

```python
class SubmissionPackageTransform(BaseTransform):
    """
    Stage 4: Package datasets for regulatory submission.
    """

    def transform(self, sdtm: dict, adam: dict, 
                  study_id: UUID, submission_type: str) -> SubmissionPackage:
        """
        1. Collect all SDTM XPT files
        2. Collect all ADaM XPT files
        3. Include Define-XML (SDTM + ADaM)
        4. Generate study-level review documents
        5. Validate eCTD structure
        6. Create ZIP/tar package
        7. Upload to S3 (submission-packages/{study_id}/{submission_id}/)
        8. Create Submission entity (status=PACKAGED)
        9. Emit submission.ready event
        10. Return SubmissionPackage with S3 paths
        """
        ...

    def validate(self, package: SubmissionPackage) -> ValidationResult:
        """
        - All required files present
        - Define-XML valid against schema
        - XPT files readable
        - No missing domains for study type
        - eCTD folder structure correct
        """
        ...
```

### 6.4 Package Structure

```
submission-packages/
└── {study_id}/
    └── {submission_id}/
        ├── define.xml                    # Define-XML metadata
        ├── sdtm/
        │   ├── dm.xpt                    # Demographics
        │   ├── ae.xpt                    # Adverse Events
        │   ├── lb.xpt                    # Lab Results
        │   ├── ex.xpt                    # Exposure
        │   └── cm.xpt                    # Concomitant Meds
        ├── adam/
        │   ├── adsl.xpt                  # Subject-Level Analysis
        │   ├── adae.xpt                  # AE Analysis
        │   └── adlb.xpt                  # Lab Analysis
        ├── review-documents/
        │   └── data-integrity-report.pdf
        └── manifest.json                 # Package manifest
```

---

## 7. Transform Engine Architecture

### 7.1 Base Transform Interface

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

TInput = TypeVar('TInput')
TOutput = TypeVar('TOutput')

class BaseTransform(ABC, Generic[TInput, TOutput]):
    """Abstract base for all transformation stages."""

    @abstractmethod
    async def transform(self, input: TInput) -> TOutput:
        """Execute the transformation."""
        ...

    @abstractmethod
    async def validate(self, input: TInput) -> ValidationResult:
        """Validate input before transformation."""
        ...

    def get_metadata(self) -> TransformMetadata:
        """Return transform metadata (name, version, stage)."""
        return TransformMetadata(
            name=self.__class__.__name__,
            version=self._version,
            stage=self._stage
        )

    async def execute(self, input: TInput) -> TransformResult[TOutput]:
        """
        Orchestrator: validate → transform → emit events.
        Subclasses override transform() and validate().
        """
        # 1. Validate
        validation = await self.validate(input)
        if not validation.is_valid:
            return TransformResult.failed(validation.errors)

        # 2. Transform
        try:
            output = await self.transform(input)
        except TransformError as e:
            return TransformResult.failed([e])

        # 3. Emit event
        await self._emit_event(output)

        return TransformResult.success(output)
```

### 7.2 Pipeline Orchestrator

```python
class TransformPipeline:
    """
    Orchestrates the full transformation pipeline.
    """

    async def run_full_pipeline(self, study_id: UUID) -> PipelineResult:
        """
        Execute all 4 stages for a study:
        1. Raw Ingest (from all adapters)
        2. Canonical Normalize
        3. CDISC Map (SDTM + ADaM)
        4. Submission Package
        """
        results = PipelineResult()

        # Stage 1: Raw Ingest
        raw_payloads = await self._run_stage1(study_id)
        results.stage1 = raw_payloads

        # Stage 2: Canonical Normalize
        canonical_entities = await self._run_stage2(raw_payloads)
        results.stage2 = canonical_entities

        # Stage 3: CDISC Mapping
        sdtm = await self._run_stage3a(canonical_entities, study_id)
        adam = await self._run_stage3b(sdtm, study_id)
        results.stage3 = {"sdtm": sdtm, "adam": adam}

        # Stage 4: Submission Packaging
        package = await self._run_stage4(sdtm, adam, study_id)
        results.stage4 = package

        return results
```

### 7.3 Error Handling

| Error Type | Behavior | Retry |
|-----------|----------|-------|
| ValidationError | Log + skip record + emit validation.failed event | No |
| TransformError | Log + emit transform.failed event | Yes (3x with backoff) |
| AdapterError | Log + emit adapter.failed event | Yes (5x with backoff) |
| FatalError | Log + halt pipeline + alert | No |

### 7.4 Transform Registry

```python
class TransformRegistry:
    """
    Registry of all available transforms.
    Enables plugin-based architecture for new source systems.
    """

    _transforms: dict[str, type[BaseTransform]] = {}

    @classmethod
    def register(cls, source_system: str, transform_class: type[BaseTransform]):
        cls._transforms[source_system] = transform_class

    @classmethod
    def get_transform(cls, source_system: str) -> BaseTransform:
        return cls._transforms[source_system]()
```

---

## 8. Data Quality Checks

### 8.1 Validation Rules (per stage)

| Stage | Check | Severity | Action |
|-------|-------|----------|--------|
| Raw Ingest | Payload non-empty | ERROR | Reject |
| Raw Ingest | Checksum match | ERROR | Reject |
| Raw Ingest | Source system known | ERROR | Reject |
| Canonical | Required fields present | ERROR | Skip record |
| Canonical | Data types correct | ERROR | Skip record |
| Canonical | Referential integrity | WARNING | Flag + continue |
| Canonical | Business rules | WARNING | Flag + continue |
| CDISC | Controlled terms valid | ERROR | Skip record |
| CDISC | SDTM variables present | ERROR | Skip record |
| CDISC | No duplicate keys | ERROR | Skip record |
| Submission | Define-XML valid | ERROR | Reject package |
| Submission | XPT files readable | ERROR | Reject package |
| Submission | eCTD structure correct | ERROR | Reject package |

### 8.2 Quality Metrics

| Metric | Target | TR Reference |
|--------|--------|--------------|
| Transform success rate | ≥99.5% | TR-003 |
| Data validation pass rate | ≥98% | TR-003 |
| Pipeline end-to-end latency | <4 hours per study | TR-003 |
| SDTM compliance rate | 100% | TR-010 |
