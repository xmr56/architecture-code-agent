# Assumptions

These assumptions fill gaps in the provided architecture and are conservative.

1. **Persistence for the slice**: The executable vertical slice uses an in-memory
   question repository. The `QuestionRepository` interface is designed so a PostgreSQL
   implementation (per `sql/game_ddl.sql`) can be swapped in without changing game logic.
   Rationale: no external DB is available at build/test time; no fake "connected" code.

2. **Answer evaluation**: For fraction answers, correctness is determined by comparing
   the reduced (simplified) fraction of the submitted answer against the stored answer.
   Whole numbers are normalized to `n/1`. Answers in `"a/b"` form and numeric form are
   accepted. This is an interpretation because the source never specifies how answers
   are graded.

3. **Identity**: `gameId`, `questionId` are integers, consistent with the OpenAPI and
   proto samples. Game creation is server-generated (starting from id 1 in the slice).

4. **State machine**: Implemented exactly as the State Diagram: `Playing -> Paused
   (pause)`, `Paused -> Playing (resume)`, `Playing -> GameOver (gameOver)`. Scoring only
   finalizes at GameOver.

5. **Infra components** (Redis, RabbitMQ, Elasticsearch, Istio, Vault, Jenkins, Terraform,
   Prometheus) are documented as architecture-level recommendations. They are intentionally
   **not** implemented or mocked in the executable slice, and no code pretends otherwise.

6. **Auth**: OAuth2 is specified for security (ASR-2). The slice does not implement OAuth2
   tokens; endpoints are unauthenticated for the demo. This is documented as a limitation.

7. **Concurrency/duration assumptions** (A1: 1000 concurrent users, A2: 1 hour/session)
   are accepted as stated and do not change the slice implementation.

8. **Requirement set**: Only FR-1, NFR-1, ASR-1 are explicitly enumerated with IDs.
   The traceability matrix maps these plus the use cases derived from the diagrams
   (View Score, Update Questions, View Help) and flags the absence of FR-2/etc.

## Open questions (unresolved, carried forward)
- Expected user growth rate?
- Expected game session length (already assumed as 1h)?
- Fraction answer grading rules (we chose simplified-fraction equality)?
- Full FR/NFR/ASR catalog (only FR-1, NFR-1, ASR-1 provided)?
