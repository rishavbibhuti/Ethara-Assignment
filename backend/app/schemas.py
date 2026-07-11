"""Pydantic schemas (request/response models)."""
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


# ---------- Project ----------
class ProjectBase(BaseModel):
    code: str
    name: str
    department: Optional[str] = None
    manager: Optional[str] = None
    status: str = "active"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    manager: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: Optional[str] = None


class Project(ProjectBase):
    id: int
    employee_count: Optional[int] = None

    class Config:
        from_attributes = True


# ---------- Seat ----------
class SeatBase(BaseModel):
    seat_number: str
    building: Optional[str] = None
    floor: Optional[str] = None
    zone: Optional[str] = None
    seat_type: str = "desk"
    status: str = "available"


class SeatCreate(SeatBase):
    pass


class SeatOccupant(BaseModel):
    id: int
    employee_code: str
    name: str

    class Config:
        from_attributes = True


class Seat(SeatBase):
    id: int
    employee: Optional[SeatOccupant] = None

    class Config:
        from_attributes = True


# ---------- Employee ----------
class EmployeeBase(BaseModel):
    employee_code: str
    name: str
    email: EmailStr
    designation: Optional[str] = None
    department: Optional[str] = None
    team: Optional[str] = None
    status: str = "active"
    join_date: Optional[date] = None
    project_id: Optional[int] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    team: Optional[str] = None
    status: Optional[str] = None
    join_date: Optional[date] = None
    project_id: Optional[int] = None


class ProjectBrief(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True


class SeatBrief(BaseModel):
    id: int
    seat_number: str
    building: Optional[str] = None
    floor: Optional[str] = None
    zone: Optional[str] = None

    class Config:
        from_attributes = True


class Employee(EmployeeBase):
    id: int
    project: Optional[ProjectBrief] = None
    seat: Optional[SeatBrief] = None

    class Config:
        from_attributes = True


class EmployeeList(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[Employee]


# ---------- Allocation ----------
class AllocateRequest(BaseModel):
    employee_id: int
    seat_id: Optional[int] = None  # if omitted, auto-assign the best available seat
    allocated_by: str = "admin"
    note: Optional[str] = None


class ReleaseRequest(BaseModel):
    employee_id: int
    released_by: str = "admin"
    note: Optional[str] = None


class AllocationHistory(BaseModel):
    id: int
    employee_id: int
    seat_id: int
    action: str
    allocated_by: str
    timestamp: datetime
    note: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Assistant ----------
class AssistantQuery(BaseModel):
    question: str


class AssistantResponse(BaseModel):
    question: str
    answer: str
    intent: str
    data: list = []
    sql_like: Optional[str] = None
