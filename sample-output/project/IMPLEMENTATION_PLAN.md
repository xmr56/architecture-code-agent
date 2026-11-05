# Implementation Plan — Space Fractions System

## Scope
Implement an executable **vertical slice** covering the principal use cases of the
Space Fractions learning game, plus the architecture deliverables required by the
analysis plan.

### Principal use cases (from Use Case Diagram)
1. **Play Game** (FR-1) — start a game, fetch fraction questions, submit answers,
   compute/return score.
2. **View Score** — retrieve a game's score.
3. **Update Questions** (admin) — add/update question definitions.
4. **View Help** — return help text.

## Components (mirroring GameComponent / QuestionComponent)
- `GameComponent` — game lifecycle, answer checking, score computation (Node.js + Express).
- `QuestionComponent` — question storage/retrieval. For the executable slice this is
  an in-memory repository with an adapter interface so PostgreSQL (per spec) can be
  plugged in without changing game logic.

## Requirements covered
- FR-1 (Play game), and the supporting use cases (View Score, Update Questions, View Help).
- Game state machine (Playing / Paused / GameOver) per State Diagram.
- Answer-check and scoring per Activity/Sequence diagrams.

## Deliverables
- Executable Node.js service (`src/`)
- `openapi.yaml` (external API contract)
- `internal.proto` (internal RPC contract)
- `k8s/spacefractions-deployment.yaml`
- `sql/game_ddl.sql` (game + question schema)
- `traceability_matrix.csv`
- `README.md`, `ASSUMPTIONS.md`
- Tests using `node:test` + `node:assert/strict` (no Jest)

## Ambiguities & gaps (resolved as conservative assumptions in ASSUMPTIONS.md)
- Requirement/ASR/NFR IDs beyond FR-1, NFR-1, ASR-1 are not enumerated in detail;
  traceability matrix will map the requirements that are actually listed and note gaps.
- The spec lists an extensive infra stack (Redis, RabbitMQ, Elasticsearch, Istio, Vault,
  Jenkins, Terraform). These are documented in architecture.md / ASSUMPTIONS.md but are
  **not** wired into the executable slice (they are deployment-time concerns outside a
  single-service vertical slice). No placeholder implementations will be faked as working.
- Question answer keys and fraction evaluation are not specified; a conservative
  exact-match + simplified-fraction evaluator is implemented and tested.
