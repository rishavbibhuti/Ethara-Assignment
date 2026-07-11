# REST API Reference

Base URL (local): `http://127.0.0.1:8000`
Interactive docs: **`/docs`** (Swagger UI) · **`/redoc`** (ReDoc)

All request/response bodies are JSON.

---

## Health
| Method | Path | Description |
|---|---|---|
| GET | `/` | Service info + docs links |
| GET | `/health` | `{ "status": "healthy" }` |

---

## Employees — `/api/employees`

### `GET /api/employees`
List, search and filter employees (paginated).

**Query params:** `q` (name/code/email), `department`, `team`, `designation`,
`status` (`active`/`new_joiner`/`inactive`), `project_id`, `has_seat` (bool),
`building`, `floor`, `page` (default 1), `page_size` (default 25, max 200).

**Response:**
```json
{
  "total": 5000, "page": 1, "page_size": 25,
  "items": [
    {
      "id": 1, "employee_code": "EMP00001", "name": "Jane Doe",
      "email": "jane.doe1@company.com", "designation": "Senior Engineer",
      "department": "Engineering", "team": "Platform", "status": "active",
      "join_date": "2021-05-03", "project_id": 3,
      "project": { "id": 3, "code": "PRJ-003", "name": "Mobile Revamp" },
      "seat": { "id": 42, "seat_number": "A3-N012", "building": "Building A", "floor": "3", "zone": "North" }
    }
  ]
}
```

### `GET /api/employees/{id}` — single employee
### `POST /api/employees` — create
```json
{ "employee_code": "EMP09001", "name": "New Hire", "email": "new.hire@company.com",
  "designation": "Associate", "department": "Engineering", "team": "Web",
  "status": "new_joiner", "project_id": 3 }
```
### `PUT /api/employees/{id}` — partial update
### `DELETE /api/employees/{id}` — delete (frees any held seat)

---

## Projects — `/api/projects`
| Method | Path | Description |
|---|---|---|
| GET | `/api/projects` | List projects (`q`, `status`, `department`) with `employee_count` |
| GET | `/api/projects/{id}` | Single project |
| POST | `/api/projects` | Create project |
| PUT | `/api/projects/{id}` | Update |
| DELETE | `/api/projects/{id}` | Delete (unassigns employees) |
| POST | `/api/projects/{id}/assign/{employee_id}` | Map an employee to a project |

---

## Seats — `/api/seats`
| Method | Path | Description |
|---|---|---|
| GET | `/api/seats` | List/search seats (`q`, `status`, `building`, `floor`, `zone`, `seat_type`, paginated) |
| GET | `/api/seats/available` | Available seats (`building`, `floor`, `zone`, `limit`) |
| GET | `/api/seats/locations` | Distinct buildings/floors/zones (for filter dropdowns) |
| GET | `/api/seats/{id}` | Single seat with occupant |
| POST | `/api/seats` | Create seat |

---

## Allocations — `/api/allocations`

### `POST /api/allocations/allocate`
Allocate a seat. Omit `seat_id` to auto-pick the best available seat (co-locates with
the employee's team when possible).
```json
{ "employee_id": 123, "seat_id": 42, "allocated_by": "admin", "note": "desk move" }
```
**Errors:** `400` if the employee already holds a seat or the seat is occupied/under
maintenance; `409` if no seats are available.

### `POST /api/allocations/release`
```json
{ "employee_id": 123, "released_by": "admin" }
```

### `POST /api/allocations/allocate-new-joiners`
Bulk auto-allocate every new joiner without a seat.
```json
{ "allocated_count": 200, "skipped_count": 0, "allocated": [ ... ], "skipped_no_seat": [] }
```

### `GET /api/allocations/history?employee_id=&limit=`
Audit log of allocate/release actions.

---

## Dashboard — `/api/dashboard`
| Method | Path | Returns |
|---|---|---|
| GET | `/api/dashboard/stats` | Headline metrics (totals, utilization %, new joiners, unseated) |
| GET | `/api/dashboard/utilization-by-building` | Per-building total/occupied/available/utilization% |
| GET | `/api/dashboard/employees-by-department` | Employee counts per department |
| GET | `/api/dashboard/employees-by-project` | Employee counts per project |
| GET | `/api/dashboard/seat-status-breakdown` | Counts per seat status |

---

## AI Assistant — `/api/assistant`

### `POST /api/assistant/query`
```json
{ "question": "How many seats are available on floor 3?" }
```
**Response:**
```json
{
  "question": "How many seats are available on floor 3?",
  "intent": "available_seats",
  "answer": "There are 265 available seats on floor 3.",
  "data": [ { "seat_number": "A3-N003", "building": "Building A", "floor": "3", "zone": "North" } ],
  "sql_like": "SELECT * FROM seats WHERE status='available' -- available seats on floor 3"
}
```

### `GET /api/assistant/examples`
Returns example questions the assistant understands.
