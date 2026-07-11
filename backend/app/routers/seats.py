"""Seat inventory: listing, search and availability."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/seats", tags=["Seats"])


@router.get("", response_model=dict)
def list_seats(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    status: Optional[str] = None,
    building: Optional[str] = None,
    floor: Optional[str] = None,
    zone: Optional[str] = None,
    seat_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
):
    query = db.query(models.Seat).options(joinedload(models.Seat.employee))
    if q:
        query = query.filter(models.Seat.seat_number.ilike(f"%{q}%"))
    if status:
        query = query.filter(models.Seat.status == status)
    if building:
        query = query.filter(models.Seat.building == building)
    if floor:
        query = query.filter(models.Seat.floor == floor)
    if zone:
        query = query.filter(models.Seat.zone == zone)
    if seat_type:
        query = query.filter(models.Seat.seat_type == seat_type)

    total = query.count()
    items = (
        query.order_by(models.Seat.seat_number)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [schemas.Seat.model_validate(s) for s in items],
    }


@router.get("/available", response_model=list[schemas.Seat])
def available_seats(
    db: Session = Depends(get_db),
    building: Optional[str] = None,
    floor: Optional[str] = None,
    zone: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
):
    query = db.query(models.Seat).filter(models.Seat.status == "available")
    if building:
        query = query.filter(models.Seat.building == building)
    if floor:
        query = query.filter(models.Seat.floor == floor)
    if zone:
        query = query.filter(models.Seat.zone == zone)
    return query.order_by(models.Seat.seat_number).limit(limit).all()


@router.get("/locations")
def seat_locations(db: Session = Depends(get_db)):
    """Distinct buildings, floors and zones for filter dropdowns."""
    buildings = [r[0] for r in db.query(models.Seat.building).distinct().all() if r[0]]
    floors = [r[0] for r in db.query(models.Seat.floor).distinct().all() if r[0]]
    zones = [r[0] for r in db.query(models.Seat.zone).distinct().all() if r[0]]
    return {
        "buildings": sorted(buildings),
        "floors": sorted(floors),
        "zones": sorted(zones),
    }


@router.get("/{seat_id}", response_model=schemas.Seat)
def get_seat(seat_id: int, db: Session = Depends(get_db)):
    seat = (
        db.query(models.Seat)
        .options(joinedload(models.Seat.employee))
        .filter(models.Seat.id == seat_id)
        .first()
    )
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    return seat


@router.post("", response_model=schemas.Seat, status_code=201)
def create_seat(payload: schemas.SeatCreate, db: Session = Depends(get_db)):
    if db.query(models.Seat).filter(models.Seat.seat_number == payload.seat_number).first():
        raise HTTPException(status_code=400, detail="Seat number already exists")
    seat = models.Seat(**payload.model_dump())
    db.add(seat)
    db.commit()
    db.refresh(seat)
    return seat
