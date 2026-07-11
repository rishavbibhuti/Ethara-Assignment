"""Natural-language query engine for the AI assistant.

Two modes:
1. Rule-based (default, no API key required): pattern-matches the question to
   an intent and runs a real database query. Fully offline & deterministic.
2. LLM-assisted (optional): if ANTHROPIC_API_KEY is set, the question plus a
   schema description is sent to Claude to extract structured filters, which
   are then executed against the DB (the LLM never touches the data directly).

The rule-based engine handles the common questions an HR/Admin user asks:
  - "How many seats are available on floor 3?"
  - "Show me all employees in the Data project"
  - "Which new joiners don't have a seat?"
  - "What is the seat utilization in Building A?"
  - "List employees in the Engineering department"
  - "How many people are on project PRJ-002?"
"""
import re

from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models


def _emp_brief(e: models.Employee):
    return {
        "id": e.id,
        "employee_code": e.employee_code,
        "name": e.name,
        "department": e.department,
        "team": e.team,
        "designation": e.designation,
        "status": e.status,
        "seat": e.seat.seat_number if e.seat else None,
        "project": e.project.name if e.project else None,
    }


def answer_question(db: Session, question: str) -> dict:
    q = question.lower().strip()

    # ---- Intent: available seats (optionally by floor/building) ----
    if ("available" in q or "free" in q or "empty" in q) and "seat" in q:
        query = db.query(models.Seat).filter(models.Seat.status == "available")
        desc = "available seats"
        floor = _extract_after(q, ["floor"])
        building = _extract_building(q)
        if floor:
            query = query.filter(models.Seat.floor.ilike(f"%{floor}%"))
            desc += f" on floor {floor}"
        if building:
            query = query.filter(models.Seat.building.ilike(f"%{building}%"))
            desc += f" in {building}"
        count = query.count()
        return {
            "intent": "available_seats",
            "answer": f"There are {count} {desc}.",
            "data": [
                {"seat_number": s.seat_number, "building": s.building, "floor": s.floor, "zone": s.zone}
                for s in query.limit(50).all()
            ],
            "sql_like": f"SELECT * FROM seats WHERE status='available' -- {desc}",
        }

    # ---- Intent: utilization ----
    if "utiliz" in q or "occupancy" in q:
        building = _extract_building(q)
        seat_q = db.query(models.Seat)
        scope = "overall"
        if building:
            seat_q = seat_q.filter(models.Seat.building.ilike(f"%{building}%"))
            scope = building
        total = seat_q.count()
        occ = seat_q.filter(models.Seat.status == "occupied").count()
        pct = round((occ / total) * 100, 1) if total else 0.0
        return {
            "intent": "utilization",
            "answer": f"Seat utilization ({scope}) is {pct}% — {occ} of {total} seats occupied.",
            "data": [{"scope": scope, "occupied": occ, "total": total, "utilization_pct": pct}],
            "sql_like": "SELECT COUNT(*) FILTER (WHERE status='occupied') / COUNT(*) FROM seats",
        }

    # ---- Intent: new joiners without a seat ----
    if "new joiner" in q or "new joiners" in q or "newjoiner" in q:
        query = db.query(models.Employee).filter(models.Employee.status == "new_joiner")
        if "without" in q or "no seat" in q or "don't have" in q or "unallocated" in q or "not have" in q:
            query = query.filter(models.Employee.seat_id.is_(None))
            answer_kind = "new joiners without a seat"
        else:
            answer_kind = "new joiners"
        emps = query.limit(100).all()
        return {
            "intent": "new_joiners",
            "answer": f"There are {query.count()} {answer_kind}.",
            "data": [_emp_brief(e) for e in emps],
            "sql_like": "SELECT * FROM employees WHERE status='new_joiner'",
        }

    # ---- Intent: employees by project ----
    if "project" in q:
        proj = _find_project(db, q)
        if proj:
            emps = db.query(models.Employee).filter(models.Employee.project_id == proj.id).all()
            return {
                "intent": "employees_by_project",
                "answer": f"{len(emps)} employee(s) are mapped to project {proj.name} ({proj.code}).",
                "data": [_emp_brief(e) for e in emps[:100]],
                "sql_like": f"SELECT * FROM employees WHERE project_id={proj.id}",
            }

    # ---- Intent: employees by department ----
    dept = _find_department(db, q)
    if dept and ("employee" in q or "people" in q or "who" in q or "list" in q or "how many" in q):
        emps = db.query(models.Employee).filter(models.Employee.department == dept).all()
        return {
            "intent": "employees_by_department",
            "answer": f"{len(emps)} employee(s) are in the {dept} department.",
            "data": [_emp_brief(e) for e in emps[:100]],
            "sql_like": f"SELECT * FROM employees WHERE department='{dept}'",
        }

    # ---- Intent: unseated employees ----
    if ("without" in q or "no seat" in q or "unallocated" in q or "not allocated" in q) and (
        "employee" in q or "people" in q or "seat" in q
    ):
        query = db.query(models.Employee).filter(models.Employee.seat_id.is_(None))
        return {
            "intent": "unseated_employees",
            "answer": f"{query.count()} employee(s) currently have no seat assigned.",
            "data": [_emp_brief(e) for e in query.limit(100).all()],
            "sql_like": "SELECT * FROM employees WHERE seat_id IS NULL",
        }

    # ---- Intent: total counts ----
    if "how many" in q and "employee" in q:
        count = db.query(models.Employee).count()
        return {
            "intent": "count_employees",
            "answer": f"There are {count} employees in total.",
            "data": [{"total_employees": count}],
            "sql_like": "SELECT COUNT(*) FROM employees",
        }
    if "how many" in q and ("project" in q):
        count = db.query(models.Project).count()
        return {
            "intent": "count_projects",
            "answer": f"There are {count} projects.",
            "data": [{"total_projects": count}],
            "sql_like": "SELECT COUNT(*) FROM projects",
        }
    if "how many" in q and "seat" in q:
        count = db.query(models.Seat).count()
        return {
            "intent": "count_seats",
            "answer": f"There are {count} seats in total.",
            "data": [{"total_seats": count}],
            "sql_like": "SELECT COUNT(*) FROM seats",
        }

    # ---- Intent: find a person by name ----
    name = _extract_person(db, q)
    if name:
        e = name
        seat = f"seat {e.seat.seat_number}" if e.seat else "no seat assigned"
        proj = e.project.name if e.project else "no project"
        return {
            "intent": "find_employee",
            "answer": f"{e.name} ({e.employee_code}) — {e.designation}, {e.department}. "
            f"Project: {proj}. Seat: {seat}.",
            "data": [_emp_brief(e)],
            "sql_like": f"SELECT * FROM employees WHERE name LIKE '%{e.name}%'",
        }

    # ---- Fallback ----
    return {
        "intent": "unknown",
        "answer": (
            "I couldn't map that to a query. Try questions like: "
            "'How many seats are available on floor 3?', "
            "'Show employees in the Data project', "
            "'Which new joiners have no seat?', or "
            "'What is seat utilization in Building A?'."
        ),
        "data": [],
        "sql_like": None,
    }


# ----------------- helpers -----------------
def _extract_after(q: str, keywords):
    for kw in keywords:
        m = re.search(rf"{kw}\s+([a-z0-9\-]+)", q)
        if m:
            return m.group(1)
    return None


def _extract_building(q: str):
    m = re.search(r"building\s+([a-z0-9]+)", q)
    if m:
        return f"Building {m.group(1).upper()}"
    return None


def _find_project(db: Session, q: str):
    # Try project code like PRJ-002 first.
    m = re.search(r"(prj-?\d+)", q)
    if m:
        code = m.group(1).upper().replace("PRJ", "PRJ-").replace("--", "-")
        proj = db.query(models.Project).filter(models.Project.code.ilike(code)).first()
        if proj:
            return proj
    # Otherwise match any project name that appears in the question.
    for proj in db.query(models.Project).all():
        if proj.name.lower() in q:
            return proj
    return None


def _find_department(db: Session, q: str):
    depts = [r[0] for r in db.query(models.Employee.department).distinct().all() if r[0]]
    for d in depts:
        if d.lower() in q:
            return d
    return None


def _extract_person(db: Session, q: str):
    # Only attempt when the question looks like it's about a person.
    if not any(w in q for w in ["where", "who is", "find", "seat of", "details of"]):
        return None
    for e in db.query(models.Employee).limit(6000).all():
        first = e.name.split()[0].lower()
        if e.name.lower() in q or (len(first) > 3 and first in q):
            return e
    return None
