# Business Requirement Template

Every BR MUST follow this template exactly. No shortcuts.

---

## BR-[NNN]: [Title]

### 1. Overview

| Field | Value |
|-------|-------|
| **BR ID** | BR-NNN |
| **Title** | [Concise title] |
| **Priority** | P0 / P1 / P2 / P3 |
| **Category** | [Data Integration / Compliance / Analytics / Workflow / Site Experience] |
| **Source Stakeholder Need(s)** | SN-xxx, SN-yyy |
| **Regulatory Basis** | [21 CFR Part 11, GDPR Article X, ICH E6(R2), etc. — or "None"] |
| **Status** | Draft / Approved / Implemented |

### 2. Business Rationale

[WHY this requirement exists. What business problem does it solve? What happens if we don't have this? Include quantified impact where possible — e.g., "Manual data reconciliation currently takes 6-8 weeks per study and costs approximately $X". 3-5 sentences minimum.]

### 3. Detailed Description

[WHAT the system must do. Written in plain language that a non-technical stakeholder can understand. Be specific — describe the behavior, not the implementation. 5-10 sentences minimum. Include:]

- The trigger or entry condition
- The expected system behavior
- The output or outcome
- Any variations by context (study phase, region, etc.)

### 4. Preconditions

[What must be true before this requirement can be fulfilled:]

- [ ] Precondition 1
- [ ] Precondition 2
- [ ] Precondition 3

### 5. Acceptance Criteria

[Measurable, testable criteria. Given/When/Then format.]

| AC ID | Criterion | Given | When | Then |
|-------|-----------|-------|------|------|
| BR-NNN-AC01 | [Short name] | [Context] | [Action] | [Expected result] |
| BR-NNN-AC02 | [Short name] | [Context] | [Action] | [Expected result] |
| BR-NNN-AC03 | [Short name] | [Context] | [Action] | [Expected result] |

Minimum 3 acceptance criteria per BR.

### 6. Dependencies

[Other BRs that must be implemented before or alongside this one.]

| Dependency | Relationship | Reason |
|-----------|-------------|--------|
| BR-XXX | Blocks / Enables / Related | [Why] |

### 7. Impacted Systems

[Which clinical systems and CDOS components are affected.]

| System | Impact Type | Description |
|--------|-----------|-------------|
| EDC | Reads from / Writes to / Syncs with | [What data] |

### 8. Data Entities Involved

[Which canonical entities are created, read, updated, or deleted.]

| Entity | Operation | Description |
|--------|----------|-------------|
| Subject | Create, Read | Subject enrollment data |

### 9. Edge Cases and Exceptions

[What happens in unusual scenarios.]

| Scenario | Expected Behavior |
|----------|------------------|
| [Edge case] | [How system handles it] |

### 10. Risks if Not Implemented

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| [Risk description] | High/Med/Low | High/Med/Low | [Alternative approach] |

### 11. Assumptions

- Assumption 1
- Assumption 2

### 12. Stakeholder Review

| Stakeholder Group | Reviewer | Status |
|------------------|----------|--------|
| Sponsor | [Name] | Pending |
| CRO | [Name] | Pending |
| Site | [Name] | Pending |
