"""SQLAlchemy ORM models for the seat allocation system."""
from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, index=True)
    manager = Column(String)
    status = Column(String, default="active", index=True)  # active | on_hold | completed
    start_date = Column(Date)
    end_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)

    employees = relationship("Employee", back_populates="project")


class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    seat_number = Column(String, unique=True, index=True, nullable=False)
    building = Column(String, index=True)
    floor = Column(String, index=True)
    zone = Column(String, index=True)
    seat_type = Column(String, default="desk")  # desk | hot_desk | cabin
    status = Column(String, default="available", index=True)  # available | occupied | reserved | maintenance

    # Current occupant (nullable). One-to-one with Employee.seat.
    employee = relationship("Employee", back_populates="seat", uselist=False)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    designation = Column(String, index=True)
    department = Column(String, index=True)
    team = Column(String, index=True)
    status = Column(String, default="active", index=True)  # active | new_joiner | inactive
    join_date = Column(Date)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    project = relationship("Project", back_populates="employees")

    seat_id = Column(Integer, ForeignKey("seats.id"), nullable=True, unique=True, index=True)
    seat = relationship("Seat", back_populates="employee")


class AllocationHistory(Base):
    __tablename__ = "allocation_history"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), index=True)
    seat_id = Column(Integer, ForeignKey("seats.id"), index=True)
    action = Column(String, index=True)  # allocated | released
    allocated_by = Column(String, default="system")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    note = Column(Text, nullable=True)
