# Database Schema

The schema is defined with SQLAlchemy in [`backend/app/models.py`](../backend/app/models.py)
and works identically on **SQLite** (default) and **PostgreSQL** (production).

## Entity-Relationship Diagram

```
                    ┌─────────────────────┐
                    │      projects       │
                    │─────────────────────│
                    │ id (PK)             │
                    │ code (unique)       │
                    │ name                │
                    │ department          │
                    │ manager             │
                    │ status              │
                    │ start_date/end_date │
                    │ description         │
                    └──────────┬──────────┘
                               │ 1
                               │
                               │ N
┌──────────────────────┐      │      ┌──────────────────────┐
│      employees        │◀─────┘      │        seats          │
│──────────────────────│             │──────────────────────│
│ id (PK)              │   1     1   │ id (PK)              │
│ employee_code(unique)│─────────────│ seat_number (unique) │
│ name                 │  seat_id    │ building             │
│ email (unique)       │  (unique FK)│ floor                │
│ designation          │             │ zone                 │
│ department           │             │ seat_type            │
│ team                 │             │ status               │
│ status               │             └──────────┬───────────┘
│ join_date            │                        │
│ project_id (FK)──────┘                        │
│ seat_id (FK)─────────────────────────────────▶│
└──────────┬───────────┘                        │
           │ N                              N    │
           │        ┌──────────────────────┐    │
           └───────▶│  allocation_history   │◀───┘
                    │──────────────────────│
                    │ id (PK)              │
                    │ employee_id (FK)     │
                    │ seat_id (FK)         │
                    │ action               │  allocated | released
                    │ allocated_by         │
                    │ timestamp            │
                    │ note                 │
                    └──────────────────────┘
```

## Tables

### `projects`
| Column | Type | Notes |
|---|---|---|
| id | Integer | PK |
| code | String | Unique, indexed (e.g. `PRJ-001`) |
| name | String | |
| department | String | Indexed |
| manager | String | |
| status | String | `active` \| `on_hold` \| `completed`, indexed |
| start_date | Date | |
| end_date | Date | Nullable |
| description | Text | Nullable |

### `seats`
| Column | Type | Notes |
|---|---|---|
| id | Integer | PK |
| seat_number | String | Unique, indexed (e.g. `A3-N012`) |
| building | String | Indexed (`Building A`…`D`) |
| floor | String | Indexed (`1`…`5`) |
| zone | String | Indexed (`North`/`South`/`East`/`West`) |
| seat_type | String | `desk` \| `hot_desk` \| `cabin` |
| status | String | `available` \| `occupied` \| `reserved` \| `maintenance`, indexed |

### `employees`
| Column | Type | Notes |
|---|---|---|
| id | Integer | PK |
| employee_code | String | Unique, indexed (e.g. `EMP00042`) |
| name | String | Indexed |
| email | String | Unique, indexed |
| designation | String | Indexed |
| department | String | Indexed |
| team | String | Indexed |
| status | String | `active` \| `new_joiner` \| `inactive`, indexed |
| join_date | Date | |
| project_id | Integer | FK → projects.id, nullable, indexed |
| seat_id | Integer | FK → seats.id, **unique**, nullable, indexed |

### `allocation_history`
| Column | Type | Notes |
|---|---|---|
| id | Integer | PK |
| employee_id | Integer | FK → employees.id, indexed |
| seat_id | Integer | FK → seats.id, indexed |
| action | String | `allocated` \| `released`, indexed |
| allocated_by | String | who performed the action |
| timestamp | DateTime | indexed |
| note | Text | Nullable |

## Relationships & Invariants
- **Employee → Project:** many-to-one (an employee belongs to at most one project).
- **Employee ↔ Seat:** one-to-one. `employees.seat_id` is **unique**, so a seat can be
  held by at most one employee, and an employee holds at most one seat.
- **AllocationHistory:** append-only audit log; one row per allocate/release action.
- **Seat status** is kept consistent with occupancy: allocating sets `occupied`,
  releasing sets `available`.

## Migrations
Tables are auto-created on startup via `Base.metadata.create_all`. For managed
PostgreSQL migrations in a larger deployment, introduce **Alembic** (not required for
this assessment).
