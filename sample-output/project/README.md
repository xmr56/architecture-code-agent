# Space Fractions — Executable Vertical Slice

An interactive fraction-learning game for sixth-grade students. This repository
implements an executable vertical slice of the **Space Fractions** system described
in the architecture analysis plan, plus the requested architecture deliverables.

## Stack
- **Language/runtime**: Node.js >= 18 (per spec)
- **Framework**: Express.js 4 (per spec)
- **Tests**: `node:test` + `node:assert/strict` (no Jest)
- **Persistence**: in-memory repository behind an interface; PostgreSQL DDL provided
  (`sql/game_ddl.sql`) for production wiring (see Assumptions).

## Setup & run

```bash
npm install
npm test          # run the test suite (node --test)
npm start         # start the API on http://localhost:3000
```

Endpoints (see `openapi.yaml` for the full contract):

| Method | Path                    | Purpose                     |
|--------|-------------------------|-----------------------------|
| GET    | `/play`                 | Start a new game (FR-1)     |
| GET    | `/games/:id/question`   | Get current question        |
| POST   | `/games/:id/answer`     | Submit an answer            |
| GET    | `/games/:id/score`      | View final score            |
| POST   | `/games/:id/pause`      | Pause game                  |
| POST   | `/games/:id/resume`     | Resume game                 |
| POST   | `/games/:id/gameover`   | End game                    |
| POST   | `/admin/questions`      | Add/update questions (admin)|
| GET    | `/help`                 | Help text                   |
| GET    | `/health`               | Health + counters           |

Example:

```bash
curl -s http://localhost:3000/play
curl -s -X POST http://localhost:3000/games/1/answer -H 'Content-Type: application/json' -d '{"answer":"3/4"}'
curl -s http://localhost:3000/games/1/score
```

## Requirement-to-file mapping

| Requirement / concern | File(s) |
|-----------------------|---------|
| FR-1 Play game | `lib/game.js`, `lib/app.js`, `server.js`, `openapi.yaml`, `internal.proto` |
| View score | `lib/game.js` (`score()`), `lib/app.js` |
| View help | `lib/app.js` (`/help`) |
| Update questions (admin) | `lib/questions.js`, `lib/app.js` (`/admin/questions`) |
| State machine (Playing/Paused/GameOver) | `lib/game.js` |
| Answer grading / fractions | `lib/fractions.js` |
| External API contract | `openapi.yaml` |
| Internal RPC contract | `internal.proto` |
| Kubernetes deployment | `k8s/spacefractions-deployment.yaml` |
| Persisted entities DDL | `sql/game_ddl.sql` |
| Traceability | `traceability_matrix.csv` |
| Plan / assumptions / limitations | `IMPLEMENTATION_PLAN.md`, `ASSUMPTIONS.md` |

## Tests

- `test/fractions.test.js` — fraction parsing/reduction/grading logic.
- `test/game.test.js` — game state machine, scoring, repository.
- `test/app.test.js` — HTTP integration of the full use-case flow.

Tests assert real application behavior (correct/incorrect grading, state transitions,
score computation, validation, HTTP status codes) — no unconditional passes.

## Limitations (honest gaps)

- **Persistence**: in-memory repositories; the PostgreSQL DDL and repository interface
  are provided but no live DB connection is implemented.
- **Auth**: OAuth2 (ASR-2) is documented, not implemented; endpoints are unauthenticated.
- **Infra stack** (Redis, RabbitMQ, Elasticsearch, Istio, Vault, Jenkins, Terraform,
  Prometheus) is documented at the architecture level, not wired into this slice.
- **Fraction grading** uses simplified-fraction equality (see `ASSUMPTIONS.md`).
- Only FR-1, NFR-1, ASR-1 are explicitly enumerated in the source requirements; the
  traceability matrix records this gap.

## Architecture deliverables included
`openapi.yaml`, `internal.proto`, `k8s/spacefractions-deployment.yaml`,
`sql/game_ddl.sql`, `traceability_matrix.csv`, plus `ASSURANCE` documentation files.
