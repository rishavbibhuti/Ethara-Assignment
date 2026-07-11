# SeatFlow — Seat Allocation & Project Mapping System

A full-stack application to manage **seat allocation** and **project mapping** for
~5,000 employees. It lets Employees, HR, Admin and Project teams manage and search
employee seating, project assignments, seat availability, utilization metrics and
new-joiner allocations — plus a natural-language **AI assistant** to query the data.

> Built with **FastAPI + SQLAlchemy** (backend) and **React + Vite + Tailwind** (frontend).
> Runs on **SQLite** out of the box (zero setup) and is **PostgreSQL-ready** via one env var.

---

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Seed Data](#seed-data)
- [API Documentation](#api-documentation)
- [AI Assistant](#ai-assistant)
- [Deployment](#deployment)
- [Additional Docs](#additional-docs)

---

## Features

| Requirement | Where |
|---|---|
| **Employee Management** | Full CRUD, list with pagination — `Employees` page & `/api/employees` |
| **Project Mapping** | Projects with team sizes, assign employees — `Projects` page & `/api/projects` |
| **Seat Allocation & Release** | Manual + auto seat assignment, release — `/api/allocations/*` |
| **New Joiner Seat Allocation** | Bulk auto-allocation with team co-location heuristic — `New Joiners` page |
| **Search & Filter** | Search employees/seats by name, code, dept, team, status, seat, building, floor, zone |
| **Dashboard & Analytics** | Utilization %, by-building, by-department, seat-status charts — `Dashboard` page |
| **AI Assistant / NL Query** | Ask questions in plain English — `AI Assistant` page & `/api/assistant/query` |
| **REST APIs** | Documented, OpenAPI/Swagger at `/docs` |
| **Seed Data Generation** | `python -m app.seed` → 5,000 employees, 5,600 seats, 40 projects |

---

## Tech Stack

- **Frontend:** React 18, Vite, Tailwind CSS, React Router, Recharts, Axios
- **Backend:** FastAPI, SQLAlchemy 2, Pydantic v2, Uvicorn
- **Database:** SQLite (default) / PostgreSQL (production) — same code, switched by `DATABASE_URL`
- **Seed data:** Faker

---

## Architecture

```
┌──────────────────┐        /api/*  (JSON REST)        ┌────────────────────┐
│  React + Vite    │  ───────────────────────────────▶ │  FastAPI            │
│  Tailwind SPA    │ ◀─────────────────────────────────│  SQLAlchemy ORM     │
│  (port 5173)     │        Vite proxy in dev           │  (port 8000)        │
└──────────────────┘                                    └─────────┬──────────┘
                                                                   │
                                                         ┌─────────▼──────────┐
                                                         │ SQLite / PostgreSQL│
                                                         └────────────────────┘
```

The AI assistant runs a **rule-based NL→query engine** server-side (fully offline,
deterministic). If `ANTHROPIC_API_KEY` is provided it can be extended to LLM-assisted
parsing — see [`backend/app/services/nl_query.py`](backend/app/services/nl_query.py).

---

## Project Structure

```
seat-allocation-system/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + routers + CORS
│   │   ├── database.py        # engine/session (SQLite or Postgres)
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── seed.py            # seed data generator
│   │   ├── routers/           # employees, projects, seats, allocations, dashboard, assistant
│   │   └── services/nl_query.py  # natural-language query engine
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/             # Dashboard, Employees, Projects, Seats, NewJoiners, Assistant
│   │   ├── components/        # Layout, ui
│   │   └── api/client.js      # axios API client
│   ├── package.json
│   ├── vercel.json
│   └── .env.example
├── docs/                      # DATABASE_SCHEMA, API, DEPLOYMENT, DEBUGGING
├── render.yaml                # Render blueprint (backend + Postgres)
├── AI_PROMPTS.md
└── README.md
```

---

## Quick Start

### Prerequisites
- Python 3.10+ and Node.js 18+

### 1. Backend

```bash
cd backend
python -m venv venv
# Windows:  venv\Scripts\activate      macOS/Linux:  source venv/bin/activate
pip install -r requirements.txt
python -m app.seed            # generate seed data (SQLite file created automatically)
uvicorn app.main:app --reload --port 8000
```

- API: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173 (Vite proxies `/api` → `http://127.0.0.1:8000`)

---

## Seed Data

```bash
cd backend
python -m app.seed           # seeds only if the DB is empty
python -m app.seed --reset   # drops & recreates all tables, then reseeds
```

Generates:
- **5,600 seats** — 4 buildings × 5 floors × 4 zones × 70 seats
- **40 projects** across departments
- **5,000 employees** — ~85% active, ~10% new joiners, ~5% inactive
- ~84% of employees allocated to seats, with matching **allocation history**

The generator uses a fixed random seed, so results are reproducible.

---

## API Documentation

Interactive Swagger UI is auto-generated at **`/docs`** and ReDoc at **`/redoc`**.
A full endpoint reference is in [`docs/API.md`](docs/API.md). Highlights:

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/employees` | List/search/filter employees (paginated) |
| POST | `/api/employees` | Create employee |
| GET | `/api/projects` | List projects with employee counts |
| GET | `/api/seats` | List/search/filter seats |
| GET | `/api/seats/available` | Available seats |
| POST | `/api/allocations/allocate` | Allocate a seat (manual or auto) |
| POST | `/api/allocations/release` | Release a seat |
| POST | `/api/allocations/allocate-new-joiners` | Bulk auto-allocate new joiners |
| GET | `/api/dashboard/stats` | Headline metrics |
| POST | `/api/assistant/query` | Natural-language query |

---

## AI Assistant

Ask questions in plain English on the **AI Assistant** page, e.g.:
- "How many seats are available on floor 3?"
- "Show me all employees in the Data Platform project"
- "Which new joiners don't have a seat?"
- "What is the seat utilization in Building A?"

Each answer includes a human summary, a result table, and the equivalent SQL-like query.

---

## Deployment

The stack deploys cleanly to free tiers. See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

- **Backend** → Render / Railway / Fly.io (Dockerfile + `render.yaml` provided). Set `DATABASE_URL` to a managed Postgres.
- **Frontend** → Vercel / Netlify (`vercel.json` provided). Set `VITE_API_BASE_URL` to the backend URL.

---

## Additional Docs
- [`AI_PROMPTS.md`](AI_PROMPTS.md) — AI tools used, prompts, outputs, manual fixes, validation
- [`docs/DATABASE_SCHEMA.md`](docs/DATABASE_SCHEMA.md) — tables, columns, relationships, ERD
- [`docs/API.md`](docs/API.md) — full REST API reference
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — deployment notes
- [`docs/DEBUGGING.md`](docs/DEBUGGING.md) — debugging notes & gotchas
