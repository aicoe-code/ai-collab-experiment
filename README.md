# Clinical Development Operating System (CDOS) — Executable Specification

A modular, executable specification for a platform that connects all systems used in clinical research, making data flow seamless, transparent, and compliant.

## Architecture

```
spec/
├── OBJECTIVE_FUNCTION.md          Acceptance criteria for each module
├── ALIGNMENT_RULES.md             Cross-module consistency rules
│
├── 01-architecture/               System architecture and tech stack
├── 02-data-models/                Canonical schemas (JSON Schema + ER + CDISC)
├── 03-transformations/            Data transform pipeline (source → target)
├── 04-integrations/               System adapters and API contracts
├── 05-trial-designs/              Trial design accommodations
├── 06-risk-models/                Operational risk and uncertainty
├── 07-compliance/                 Regulatory and security requirements
└── 08-implementation/             Roadmap, cost model, success metrics
```

## How This Was Built

Each module was authored by an independent AI agent following shared alignment rules.
A meta-agent verified cross-module consistency. A review agent scored against the objective function.

## Iteration History

See git log for the full history of changes and PR reviews.
