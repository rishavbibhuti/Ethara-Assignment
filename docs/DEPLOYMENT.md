# Deployment Notes

The app is designed to deploy to free/hobby tiers. Recommended split:
**backend on Render/Railway/Fly.io**, **frontend on Vercel/Netlify**, **PostgreSQL** as
a managed database.

---

## 1. Database (PostgreSQL)
Provision a managed Postgres (Render, Railway, Neon, Supabase, etc.) and copy its
connection string. It must be in SQLAlchemy form:

```
postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME
```

> If your provider gives `postgres://…`, change the scheme to
> `postgresql+psycopg2://…`. Uncomment `psycopg2-binary` in `backend/requirements.txt`.

---

## 2. Backend (Render example)

A `render.yaml` blueprint is at the repo root and a `Dockerfile` is in `backend/`.
The blueprint provisions the web service **and** a free Postgres, and seeds the DB
on deploy — so "New + → Blueprint" is the fastest path.

**Render (Docker or native Python):**
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variables:
  - `DATABASE_URL` = your Postgres URL
  - `CORS_ORIGINS` = your frontend URL, e.g. `https://seatflow.vercel.app`

**Seed the production DB once** (from a Render shell or locally pointed at the prod DB):
```bash
DATABASE_URL=postgresql+psycopg2://... python -m app.seed --reset
```

**Railway / Fly.io:** same idea — set `DATABASE_URL`, `CORS_ORIGINS`, and the start
command above. The `Dockerfile` works on any container platform.

---

## 3. Frontend (Vercel example)

A `vercel.json` is included in `frontend/`.

- Framework preset: **Vite**
- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Environment variable:
  - `VITE_API_BASE_URL` = your deployed backend URL, e.g. `https://seatflow-api.onrender.com`

**Netlify:** build command `npm run build`, publish directory `dist`, same env var.
The included `vercel.json` adds an SPA rewrite so client-side routes (e.g. `/employees`)
resolve to `index.html`.

---

## 4. Post-deploy checklist
- [ ] Backend `/health` returns `{"status":"healthy"}`
- [ ] Backend `/docs` loads (Swagger)
- [ ] `DATABASE_URL` points at Postgres and the DB is seeded
- [ ] `CORS_ORIGINS` includes the exact frontend origin (no trailing slash)
- [ ] Frontend `VITE_API_BASE_URL` points at the backend and was set **before** `npm run build`
- [ ] Dashboard loads real numbers; AI assistant returns answers

---

## URLs to submit
Fill these in after deploying:
- **GitHub Repository:** `https://github.com/<you>/seat-allocation-system`
- **Live Frontend:** `https://<your-frontend>.vercel.app`
- **Live Backend:** `https://<your-backend>.onrender.com`
- **Swagger:** `https://<your-backend>.onrender.com/docs`
