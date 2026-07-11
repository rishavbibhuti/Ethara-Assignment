# AI Usage Documentation

This project was built with the assistance of **Claude (Anthropic)** acting as a
pair-programming agent. This document records the prompts used, what was generated,
the manual fixes applied, and how each part was validated — as required by the
assessment.

---

## Tooling
- **AI tool:** Claude (Claude Code agent)
- **Human role:** Requirements definition, architectural decisions, review of every
  file, running the code, verifying behavior, and fixing issues found during testing.

---

## Prompt 1 — Project scaffolding & stack decision

**Prompt (paraphrased):**
> Build a full-stack seat allocation & project mapping app for ~5,000 employees, with
> a `frontend` and `backend` folder. Requirements: employee management, project mapping,
> seat allocation/release, new-joiner allocation, search & filter, dashboard/analytics,
> an AI natural-language query interface, REST APIs and seed data. Recommended stack:
> React/Next + Tailwind, FastAPI, PostgreSQL.

**Output generated:** Folder layout, tech-stack recommendation.

**Decisions made (human):**
- **SQLite by default, PostgreSQL-ready** via `DATABASE_URL`, so the project runs with
  zero external setup on any machine but deploys to Postgres unchanged.
- **React + Vite** instead of Next.js — the app is a client-side dashboard with no SSR
  need; Vite is faster to run and deploy as a static site.

**Validation:** Confirmed the directory structure and that both apps start.

---

## Prompt 2 — Data model & SQLAlchemy models

**Prompt:**
> Design the database schema: employees, projects, seats, and an allocation-history
> audit table. An employee has at most one seat; a seat has at most one occupant.

**Output:** `models.py` with `Employee`, `Project`, `Seat`, `AllocationHistory`,
relationships, indexes, and status enums (as strings).

**Manual fixes:**
- Added a `unique=True` constraint on `Employee.seat_id` to enforce one-seat-per-employee
  at the DB level.
- Indexed the columns used by filters (`department`, `team`, `status`, `building`,
  `floor`, `zone`) for query performance at 5k+ rows.

**Validation:** Ran the seed script and inspected row counts and FK integrity.

---

## Prompt 3 — REST API routers

**Prompt:**
> Implement FastAPI routers for employees (CRUD + search/filter + pagination),
> projects, seats (with availability & location filters), allocations
> (allocate/release/auto), and a dashboard analytics router.

**Output:** `routers/*.py`, Pydantic `schemas.py`, and business rules in
`allocations.py` (reject double-allocation, free seat on release, co-locate new joiners
with their team, write allocation history).

**Manual fixes:**
- Removed a broken/portable-unsafe `func.cast(... )` aggregation in the dashboard
  `utilization-by-building` endpoint and replaced it with explicit per-building counts
  that work identically on SQLite and PostgreSQL.
- Added `db.flush()` inside the new-joiner bulk loop so each subsequent seat pick sees
  seats taken earlier in the same request (prevented double-assigning one seat).

**Validation:** `curl` tests against every endpoint (allocate → release round-trip,
pagination, filters, analytics) — all returned expected results. See `docs/DEBUGGING.md`.

---

## Prompt 4 — Natural-language AI assistant

**Prompt:**
> Build a natural-language query endpoint that answers questions like "how many seats
> are available on floor 3", "which new joiners have no seat", "seat utilization in
> Building A", without requiring an external API key.

**Output:** `services/nl_query.py` — an intent-matching engine that maps a question to
a real DB query and returns an answer, a data table, and an equivalent SQL-like string.

**Manual fixes:**
- Ordered intent checks so specific patterns (new-joiners-without-seat) are tested
  before general ones (all new joiners), avoiding mis-classification.
- Added building/floor extraction via regex and a project-code parser (`PRJ-002`).
- Documented that setting `ANTHROPIC_API_KEY` is the extension point for LLM-assisted
  parsing (the LLM extracts filters; the DB is still the source of truth).

**Validation:** Tested each documented example question end-to-end via the API and the UI;
verified counts matched direct DB queries.

---

## Prompt 5 — Seed data generator

**Prompt:**
> Generate realistic seed data: ~5,000 employees, ~5,600 seats across buildings/floors/
> zones, ~40 projects, a realistic mix of statuses, and matching allocation history.

**Output:** `seed.py` using Faker with bulk inserts.

**Manual fixes:**
- Switched from row-by-row ORM inserts to `bulk_insert_mappings` for speed at 5k+ rows.
- Chunked the "mark occupied" `IN (...)` update to stay under SQLite's variable limit
  (`too many SQL variables` error was hit at ~4k ids; fixed with 900-id chunks).
- Fixed `Faker.seed` usage for reproducible datasets.

**Validation:** Ran `python -m app.seed --reset`; confirmed 5,000 / 5,600 / 40 counts
and that occupied + available + reserved + maintenance = total seats.

---

## Prompt 6 — React frontend

**Prompt:**
> Build a Tailwind UI: sidebar layout, dashboard with charts (Recharts), employees page
> with search/filter/pagination and allocate/release actions, projects, seats grid,
> new-joiner allocation page, and a chat-style AI assistant page.

**Output:** Vite React app, `pages/*`, `components/*`, axios client, Tailwind config.

**Manual fixes:**
- Configured the Vite dev proxy (`/api` → `127.0.0.1:8000`) so the frontend needs no
  CORS juggling in development, and `VITE_API_BASE_URL` for production.
- Made the assistant render arbitrary result tables by reading keys off the first row.

**Validation:** `npm run build` succeeded; ran the dev server and verified the dashboard,
assistant (live query "seats available on floor 3" returned 265), and employees pages in
the browser with **no console errors**.

---

## Summary of validation methods
- **Unit-level:** `curl`/HTTP checks on every endpoint.
- **Integration:** allocate→release round-trips; new-joiner bulk allocation; NL queries
  cross-checked against direct DB counts.
- **Frontend:** production build + live browser walkthrough with console-error check.
- **Data integrity:** seat status invariants and FK relationships verified after seeding.

Every AI-generated file was read and reviewed by a human before being kept; the fixes
above are the concrete changes made on top of first-pass AI output.
