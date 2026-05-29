# CDOS Full SDLC — Alignment Rules

Every artifact author MUST read this file first. These rules ensure cross-artifact consistency.

---

## 1. Requirement ID Conventions

| Level | Format | Example |
|-------|--------|---------|
| Business Requirement | BR-NNN | BR-001, BR-042 |
| Functional Requirement | FR-NNN | FR-001, FR-156 |
| Technical Requirement / NFR | TR-NNN | TR-001, TR-030 |
| Use Case | UC-NNN | UC-001, UC-010 |
| Test Case | TC-NNN | TC-001, TC-200 |
| Architecture Decision Record | ADR-NNN | ADR-001 |

When referencing a requirement from another artifact, use the full ID:
"This implements FR-015 (defined in 02-functional-requirements/functional-requirements.md)"

---

## 2. Canonical Entity Names

Use EXACTLY these names (case-sensitive) across ALL artifacts:

| Canonical Name | Abbreviation | Description |
|---------------|-------------|-------------|
| Study | study | A clinical trial |
| Subject | subj | A participant enrolled in a study |
| Site | site | A clinical investigation site |
| Investigator | inv | A principal/sub-investigator |
| Visit | visit | A scheduled study visit |
| AdverseEvent | ae | An adverse event |
| LabResult | lab | A laboratory test result |
| Medication | med | A concomitant/study medication |
| Protocol | proto | Study protocol metadata |
| Dose | dose | A dose of study drug |
| Query | query | A data clarification request |
| CRFPage | crf | A case report form page |
| Sample | sample | A biological specimen |
| Submission | subm | A regulatory submission artifact |

Do NOT use synonyms. "Patient" → Subject. "Facility" → Site.

---

## 3. Canonical System Names

| Canonical Name | Category | Real Products |
|---------------|----------|--------------|
| EDC | Data Capture | Medidata Rave, Oracle InForm, Veeva Vault CDMS, Castor |
| CTMS | Trial Management | Oracle Siebel CTMS, Medidata CTMS, Veeva Vault CTMS |
| LIMS | Laboratory | Medidata Rave Lab, Covance LIMS, ICON LIMS |
| eTMF | Document Mgmt | Veeva Vault eTMF, Montrium, Florence eBinders |
| Safety | Pharmacovigilance | Argus Safety, ArisGlobal, Oracle AERS |
| IWRS | Randomization | Signant Health, 4G Clinical, Medidata RTSM |
| eCOA | Outcomes | ERT, Clario, Medidata Patient Cloud |
| Imaging | Medical Imaging | BioClinica, Parexel Imaging |
| Wearables | IoT/Sensors | ActiGraph, Verily, Apple HealthKit |
| RegSubmit | Regulatory | Veeva Vault RIM, Lorenz docuBridge |

---

## 4. CDISC Terminology

| Term | Standard |
|------|----------|
| SDTM v3.4 | Study Data Tabulation Model |
| ADaM v2.1 | Analysis Data Model |
| ODM v2.0 | Operational Data Model |
| CDASH v2.1 | Clinical Data Acquisition Standards |
| Define-XML v2.1 | Metadata specification |

SDTM domain codes: 2-character uppercase (DM, AE, LB, EX, CM)

---

## 5. Python Code Conventions

### 5a. Project Layout
```
08-software/
├── services/
│   ├── core/              # Core business services
│   │   └── study_service.py
│   ├── adapters/          # External system adapters
│   │   ├── base_adapter.py    # Abstract interface
│   │   └── edc_adapter.py     # Concrete implementation
│   └── transforms/        # Data transformation engine
│       ├── base_transform.py  # Abstract interface
│       └── edc_to_sdtm.py     # Concrete implementation
├── api-gateway/
│   └── app.py             # FastAPI application
├── event-bus/
│   ├── base_bus.py        # Abstract event bus interface
│   └── kafka_bus.py       # Kafka implementation
├── shared/
│   ├── models/            # Pydantic models (match JSON Schemas)
│   │   ├── study.py
│   │   └── subject.py
│   └── utils/             # Common utilities
│       ├── config.py
│       ├── logging.py
│       └── errors.py
├── infrastructure/
│   ├── terraform/
│   └── k8s/
└── tests/
```

### 5b. Naming Conventions
- Files: snake_case (e.g., `edc_adapter.py`)
- Classes: PascalCase (e.g., `EDCAdapter`)
- Functions/methods: snake_case (e.g., `get_subject_by_id`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_RETRY_COUNT`)
- Private: prefixed with underscore (e.g., `_validate_crf`)

### 5c. Interface Pattern
All adapters and transforms use abstract base classes:
```python
from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    @abstractmethod
    async def connect(self) -> None: ...
    @abstractmethod
    async def fetch_subjects(self, study_id: str) -> list[Subject]: ...
```

### 5d. Pydantic Model Pattern
Models must match JSON Schema definitions:
```python
from pydantic import BaseModel, Field
from uuid import UUID

class Subject(BaseModel):
    subject_id: UUID
    study_id: UUID
    site_id: UUID
    status: SubjectStatus
    # ... matches subject.json schema
```

---

## 6. JSON Schema Format

Each entity definition in 05-data-models/canonical/:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://cdos.io/schemas/subject.json",
  "title": "Subject",
  "type": "object",
  "required": ["subject_id", "study_id", "site_id", "status"],
  "properties": {
    "subject_id": { "type": "string", "format": "uuid" }
  }
}
```

---

## 7. OpenAPI Format

```yaml
openapi: 3.1.0
info:
  title: CDOS Core API
  version: 1.0.0
paths:
  /studies/{study_id}/subjects:
    get:
      operationId: listSubjects
      parameters:
        - name: study_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: List of subjects
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SubjectList'
```

---

## 8. AsyncAPI Format

```yaml
asyncapi: 3.0.0
info:
  title: CDOS Events
  version: 1.0.0
channels:
  subject.enrolled:
    address: subject.enrolled
    messages:
      SubjectEnrolled:
        $ref: '#/components/messages/SubjectEnrolled'
```

---

## 9. Test Format

```python
import pytest

class TestSubjectEnrollment:
    """Tests for FR-015: Subject enrollment workflow."""

    def test_enroll_subject_success(self):
        """TC-042: Subject enrolls with valid eligibility."""
        # Given: a screened subject with passing eligibility
        # When: enrollment is submitted
        # Then: subject status changes to ENROLLED
        ...

    def test_enroll_subject_ineligible(self):
        """TC-043: Subject fails eligibility criteria."""
        ...
```

---

## 10. Traceability Format

Requirements traceability matrix in 09-sdlc-traceability/:

```markdown
| BR | FR | TR | Design | Test | Code |
|----|----|----|--------|------|------|
| BR-001 | FR-001, FR-002 | TR-001 | architecture.md#L42 | TC-001, TC-002 | study_service.py |
| BR-002 | FR-003 | TR-002 | api-design.md#L15 | TC-003 | edc_adapter.py |
```

---

## 11. Shared Abbreviations

| Abbrev | Full |
|--------|------|
| BR | Business Requirement |
| FR | Functional Requirement |
| TR | Technical Requirement (NFR) |
| UC | Use Case |
| TC | Test Case |
| CRF | Case Report Form |
| SAE | Serious Adverse Event |
| SUSAR | Suspected Unexpected Serious Adverse Reaction |
| eCTD | Electronic Common Technical Document |
| ICSR | Individual Case Safety Report |
| GCP | Good Clinical Practice |
| CSV | Computer System Validation |
| RWD/RWE | Real-World Data / Evidence |
| EHR | Electronic Health Record |
