"""Project mapping: CRUD and employee assignment."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.get("", response_model=list[schemas.Project])
def list_projects(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    status: Optional[str] = None,
    department: Optional[str] = None,
):
    query = db.query(models.Project)
    if q:
        like = f"%{q}%"
        query = query.filter(
            models.Project.name.ilike(like) | models.Project.code.ilike(like)
        )
    if status:
        query = query.filter(models.Project.status == status)
    if department:
        query = query.filter(models.Project.department == department)

    projects = query.order_by(models.Project.name).all()

    # Attach employee counts.
    counts = dict(
        db.query(models.Employee.project_id, func.count(models.Employee.id))
        .group_by(models.Employee.project_id)
        .all()
    )
    result = []
    for p in projects:
        data = schemas.Project.model_validate(p)
        data.employee_count = counts.get(p.id, 0)
        result.append(data)
    return result


@router.get("/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    data = schemas.Project.model_validate(p)
    data.employee_count = (
        db.query(models.Employee).filter(models.Employee.project_id == project_id).count()
    )
    return data


@router.post("", response_model=schemas.Project, status_code=201)
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db)):
    if db.query(models.Project).filter(models.Project.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Project code already exists")
    p = models.Project(**payload.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.put("/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int, payload: schemas.ProjectUpdate, db: Session = Depends(get_db)
):
    p = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    # Unassign employees from this project.
    db.query(models.Employee).filter(models.Employee.project_id == project_id).update(
        {models.Employee.project_id: None}
    )
    db.delete(p)
    db.commit()
    return None


@router.post("/{project_id}/assign/{employee_id}", response_model=schemas.Employee)
def assign_employee(project_id: int, employee_id: int, db: Session = Depends(get_db)):
    p = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.project_id = project_id
    db.commit()
    db.refresh(emp)
    return emp
