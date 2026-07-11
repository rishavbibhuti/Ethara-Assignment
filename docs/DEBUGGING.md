# Debugging Notes

Issues encountered while building and testing the system, and how they were resolved.

---

### 1. SQLite "too many SQL variables" during seeding
**Symptom:** Bulk-updating ~4,000 seats to `occupied` with a single
`WHERE id IN (...)` failed on SQLite (default variable limit ~999).
**Fix:** Chunk the id list into batches of 900 in `seed.py` before the `IN (...)`
update. Works on both SQLite and Postgres.

---

### 2. New-joiner bulk allocation assigning the same seat twice
**Symptom:** In `allocate-new-joiners`, two joiners could be handed the same seat
because the seat's `occupied` status wasn't visible to the next iteration within the
same transaction.
**Fix:** Call `db.flush()` after each allocation inside the loop so subsequent
`_pick_seat_for_employee` queries exclude the just-taken seat.

---

### 3. Non-portable aggregation in utilization endpoint
**Symptom:** An initial `func.sum(func.cast(status == 'occupied', ...))` expression was
fragile across SQLite/Postgres.
**Fix:** Replaced with explicit per-building `COUNT` queries in
`dashboard/utilization-by-building` — identical results, portable everywhere.

---

### 4. AI assistant mis-classifying "new joiners without a seat"
**Symptom:** The general "new joiners" intent matched before the more specific
"new joiners without a seat" branch, so the seat filter was ignored.
**Fix:** Check the "without/no seat/unallocated" qualifier inside the new-joiner
intent and apply `seat_id IS NULL` accordingly. Ordered specific intents before
general ones.

---

### 5. CORS in development
**Symptom:** Direct browser calls from `localhost:5173` to `127.0.0.1:8000` would
otherwise need CORS configuration.
**Fix:** Vite dev server proxies `/api` → `http://127.0.0.1:8000` (see
`vite.config.js`), so the browser only ever talks to its own origin in dev. In
production, `CORS_ORIGINS` on the backend whitelists the deployed frontend.

---

### 6. Python 3.13 dependency wheels
**Symptom:** Hard-pinned older package versions had no prebuilt wheels for Python 3.13.
**Fix:** Loosened `requirements.txt` to compatible ranges; `psycopg2-binary` is
commented out and only needed for Postgres.

---

### 7. `datetime.utcnow()` deprecation warning
**Symptom:** Python 3.13 warns that `datetime.utcnow()` is deprecated.
**Status:** Harmless (the value is still correct). Noted for a future cleanup to
`datetime.now(datetime.UTC)`.

---

## How to reproduce the validation
```bash
# Backend
cd backend && python -m app.seed --reset && uvicorn app.main:app --port 8000

# Smoke tests
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/dashboard/stats
curl -X POST http://127.0.0.1:8000/api/assistant/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the seat utilization in Building A?"}'

# Frontend
cd frontend && npm install && npm run dev   # open http://localhost:5173
```
