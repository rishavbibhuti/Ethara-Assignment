"""Seat allocation, release, and new-joiner auto-allocation.

Business rules
--------------
* An employee can hold at most one seat.
* A seat can hold at most one employee (status becomes "occupied").
* Allocating to an already-occupied seat is rejected.
* Releasing frees the seat (status -> "available") and clears the link.
* Auto-allocation prefers a seat in the same building/floor as the employee's
  team-mates, then falls back to any available seat.
* Every allocate/release is recorded in AllocationHistory for auditing.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/allocations", tags=["Allocations"])


def _pick_seat_for_employee(db: Session, emp: models.Employee):
    """Heuristic: co-locate with the employee's team, else any free seat."""
    if emp.team:
        # Find the most common building/floor for this team.
        loc = (
            db.query(models.Seat.building, models.Seat.floor, func.count(models.Seat.id))
            .join(models.Employee, models.Employee.seat_id == models.Seat.id)
            .filter(models.Employee.team == emp.team)
            .group_by(models.Seat.building, models.Seat.floor)
            .order_by(func.count(models.Seat.id).desc())
            .first()
        )
        if loc:
            building, floor, _ = loc
            seat = (
                db.query(models.Seat)
                .filter(
                    models.Seat.status == "available",
                    models.Seat.building == building,
                    models.Seat.floor == floor,
                )
                .order_by(models.Seat.seat_number)
                .first()
            )
            if seat:
                return seat
    return (
        db.query(models.Seat)
        .filter(models.Seat.status == "available")
        .order_by(models.Seat.seat_number)
        .first()
    )


@router.post("/allocate", response_model=schemas.Employee)
def allocate_seat(payload: schemas.AllocateRequest, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == payload.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    if emp.seat_id:
        raise HTTPException(
            status_code=400,
            detail=f"Employee already holds seat {emp.seat.seat_number}. Release it first.",
        )

    if payload.seat_id:
        seat = db.query(models.Seat).filter(models.Seat.id == payload.seat_id).first()
        if not seat:
            raise HTTPException(status_code=404, detail="Seat not found")
        if seat.status == "occupied":
            raise HTTPException(status_code=400, detail="Seat is already occupied")
        if seat.status == "maintenance":
            raise HTTPException(status_code=400, detail="Seat is under maintenance")
    else:
        seat = _pick_seat_for_employee(db, emp)
        if not seat:
            raise HTTPException(status_code=409, detail="No available seats")

    seat.status = "occupied"
    emp.seat_id = seat.id
    db.add(
        models.AllocationHistory(
            employee_id=emp.id,
            seat_id=seat.id,
            action="allocated",
            allocated_by=payload.allocated_by,
            note=payload.note,
        )
    )
    db.commit()
    db.refresh(emp)
    return (
        db.query(models.Employee)
        .options(joinedload(models.Employee.project), joinedload(models.Employee.seat))
        .filter(models.Employee.id == emp.id)
        .first()
    )


@router.post("/release", response_model=schemas.Employee)
def release_seat(payload: schemas.ReleaseRequest, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == payload.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    if not emp.seat_id:
        raise HTTPException(status_code=400, detail="Employee has no seat to release")

    seat = db.query(models.Seat).filter(models.Seat.id == emp.seat_id).first()
    if seat:
        seat.status = "available"
    db.add(
        models.AllocationHistory(
            employee_id=emp.id,
            seat_id=emp.seat_id,
            action="released",
            allocated_by=payload.released_by,
            note=payload.note,
        )
    )
    emp.seat_id = None
    db.commit()
    db.refresh(emp)
    return (
        db.query(models.Employee)
        .options(joinedload(models.Employee.project), joinedload(models.Employee.seat))
        .filter(models.Employee.id == emp.id)
        .first()
    )


@router.post("/allocate-new-joiners", response_model=dict)
def allocate_new_joiners(db: Session = Depends(get_db)):
    """Bulk auto-allocate every new joiner that lacks a seat."""
    joiners = (
        db.query(models.Employee)
        .filter(models.Employee.status == "new_joiner", models.Employee.seat_id.is_(None))
        .all()
    )
    allocated, skipped = [], []
    for emp in joiners:
        seat = _pick_seat_for_employee(db, emp)
        if not seat:
            skipped.append(emp.employee_code)
            continue
        seat.status = "occupied"
        emp.seat_id = seat.id
        db.add(
            models.AllocationHistory(
                employee_id=emp.id,
                seat_id=seat.id,
                action="allocated",
                allocated_by="auto-new-joiner",
                note="Auto-allocated on onboarding",
            )
        )
        allocated.append({"employee": emp.employee_code, "seat": seat.seat_number})
        db.flush()  # keep subsequent picks aware of the newly-taken seat
    db.commit()
    return {
        "allocated_count": len(allocated),
        "skipped_count": len(skipped),
        "allocated": allocated,
        "skipped_no_seat": skipped,
    }


@router.get("/history", response_model=list[schemas.AllocationHistory])
def allocation_history(
    db: Session = Depends(get_db), employee_id: int | None = None, limit: int = 100
):
    query = db.query(models.AllocationHistory)
    if employee_id:
        query = query.filter(models.AllocationHistory.employee_id == employee_id)
    return query.order_by(models.AllocationHistory.timestamp.desc()).limit(limit).all()
