"""Dashboard and analytics endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    total_employees = db.query(models.Employee).count()
    total_seats = db.query(models.Seat).count()
    occupied = db.query(models.Seat).filter(models.Seat.status == "occupied").count()
    available = db.query(models.Seat).filter(models.Seat.status == "available").count()
    reserved = db.query(models.Seat).filter(models.Seat.status == "reserved").count()
    maintenance = db.query(models.Seat).filter(models.Seat.status == "maintenance").count()
    new_joiners = db.query(models.Employee).filter(
        models.Employee.status == "new_joiner"
    ).count()
    unseated = db.query(models.Employee).filter(models.Employee.seat_id.is_(None)).count()
    total_projects = db.query(models.Project).count()

    utilization = round((occupied / total_seats) * 100, 1) if total_seats else 0.0
    return {
        "total_employees": total_employees,
        "total_seats": total_seats,
        "occupied_seats": occupied,
        "available_seats": available,
        "reserved_seats": reserved,
        "maintenance_seats": maintenance,
        "utilization_pct": utilization,
        "new_joiners": new_joiners,
        "unseated_employees": unseated,
        "total_projects": total_projects,
    }


@router.get("/utilization-by-building")
def utilization_by_building(db: Session = Depends(get_db)):
    result = []
    buildings = [r[0] for r in db.query(models.Seat.building).distinct().all() if r[0]]
    for b in sorted(buildings):
        total = db.query(models.Seat).filter(models.Seat.building == b).count()
        occ = (
            db.query(models.Seat)
            .filter(models.Seat.building == b, models.Seat.status == "occupied")
            .count()
        )
        result.append(
            {
                "building": b,
                "total": total,
                "occupied": occ,
                "available": total - occ,
                "utilization_pct": round((occ / total) * 100, 1) if total else 0.0,
            }
        )
    return result


@router.get("/employees-by-department")
def employees_by_department(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Employee.department, func.count(models.Employee.id))
        .group_by(models.Employee.department)
        .order_by(func.count(models.Employee.id).desc())
        .all()
    )
    return [{"department": r[0] or "Unassigned", "count": r[1]} for r in rows]


@router.get("/employees-by-project")
def employees_by_project(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Project.name, func.count(models.Employee.id))
        .outerjoin(models.Employee, models.Employee.project_id == models.Project.id)
        .group_by(models.Project.name)
        .order_by(func.count(models.Employee.id).desc())
        .all()
    )
    return [{"project": r[0], "count": r[1]} for r in rows]


@router.get("/seat-status-breakdown")
def seat_status_breakdown(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Seat.status, func.count(models.Seat.id))
        .group_by(models.Seat.status)
        .all()
    )
    return [{"status": r[0], "count": r[1]} for r in rows]
