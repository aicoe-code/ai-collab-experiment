# Clinical Development Operating System (CDOS) — Full SDLC Artifact Set

A complete software development lifecycle artifact set for a platform that connects all systems used in clinical research, making data flow seamless, transparent, and compliant.

## Technology Stack

- **Language**: Python 3.11+
- **API Framework**: FastAPI (REST) + Confluent Kafka (events)
- **Database**: PostgreSQL 15+ with pgvector extension
- **ORM**: SQLAlchemy 2.0 + Alembic migrations
- **Validation**: Pydantic v2
- **Testing**: pytest + pytest-asyncio + httpx
- **Infrastructure**: Terraform + Kubernetes (Helm)
- **API Specs**: OpenAPI 3.1 + AsyncAPI 3.0

## Artifact Structure

| Directory | SDLC Phase | Key Artifacts |
|-----------|-----------|---------------|
| 01-business-requirements/ | BR | Stakeholder needs, business requirements, use cases |
| 02-functional-requirements/ | FR | Functional requirements, acceptance criteria, data flows |
| 03-technical-requirements/ | TR | NFRs, infrastructure, compliance, integration requirements |
| 04-technical-design/ | Design | Architecture, data model design, API design, security |
| 05-data-models/ | Schema | JSON Schema, SQL DDL, Alembic migrations, seed data |
| 06-api-specifications/ | Contracts | OpenAPI 3.1, AsyncAPI 3.0, GraphQL schemas |
| 07-test-artifacts/ | QA | Test plan, unit/integration/e2e/perf/validation tests |
| 08-software/ | Code | Services, adapters, transforms, gateway, infra, tests |
| 09-sdlc-traceability/ | Governance | Requirements traceability, ADRs, change log |

## Multi-Agent Build Process

Each artifact set was authored by an independent AI agent following shared alignment rules.
A meta-agent verified cross-artifact consistency. A review agent scored against the objective function.

See git log for the full history of changes and PR reviews.
