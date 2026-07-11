"""Employee management: CRUD, search and filtering."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/employees", tags=["Employees"])


@router.get("", response_model=schemas.EmployeeList)
def list_employees(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Free-text search over name, code, email"),
    department: Optional[str] = None,
    team: Optional[str] = None,
    designation: Optional[str] = None,
    status: Optional[str] = None,
    project_id: Optional[int] = None,
    has_seat: Optional[bool] = Query(None, description="Filter by whether the employee has a seat"),
    building: Optional[str] = None,
    floor: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
):
    query = db.query(models.Employee).options(
        joinedload(models.Employee.project), joinedload(models.Employee.seat)
    )

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                models.Employee.name.ilike(like),
                models.Employee.employee_code.ilike(like),
                models.Employee.email.ilike(like),
            )
        )
    if department:
        query = query.filter(models.Employee.department == department)
    if team:
        query = query.filter(models.Employee.team == team)
    if designation:
        query = query.filter(models.Employee.designation == designation)
    if status:
        query = query.filter(models.Employee.status == status)
    if project_id is not None:
        query = query.filter(models.Employee.project_id == project_id)
    if has_seat is True:
        query = query.filter(models.Employee.seat_id.isnot(None))
    elif has_seat is False:
        query = query.filter(models.Employee.seat_id.is_(None))
    if building or floor:
        query = query.join(models.Seat, models.Employee.seat_id == models.Seat.id)
        if building:
            query = query.filter(models.Seat.building == building)
        if floor:
            query = query.filter(models.Seat.floor == floor)

    total = query.count()
    items = (
        query.order_by(models.Employee.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/{employee_id}", response_model=schemas.Employee)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = (
        db.query(models.Employee)
        .options(joinedload(models.Employee.project), joinedload(models.Employee.seat))
        .filter(models.Employee.id == employee_id)
        .first()
    )
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@router.post("", response_model=schemas.Employee, status_code=201)
def create_employee(payload: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    if db.query(models.Employee).filter(models.Employee.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    if db.query(models.Employee).filter(
        models.Employee.employee_code == payload.employee_code
    ).first():
        raise HTTPException(status_code=400, detail="Employee code already exists")
    emp = models.Employee(**payload.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@router.put("/{employee_id}", response_model=schemas.Employee)
def update_employee(
    employee_id: int, payload: schemas.EmployeeUpdate, db: Session = Depends(get_db)
):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(emp, key, value)
    db.commit()
    db.refresh(emp)
    return emp


@router.delete("/{employee_id}", status_code=204)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    # Free the seat if held.
    if emp.seat_id:
        seat = db.query(models.Seat).filter(models.Seat.id == emp.seat_id).first()
        if seat:
            seat.status = "available"
    db.delete(emp)
    db.commit()
    return None
