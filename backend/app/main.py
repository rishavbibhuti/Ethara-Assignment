"""FastAPI application entrypoint for the Seat Allocation & Project Mapping system."""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import Base, engine
from .routers import allocations, assistant, dashboard, employees, projects, seats

# Create tables on startup (idempotent). For real Postgres migrations use Alembic.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Seat Allocation & Project Mapping API",
    description=(
        "REST API to manage seat allocation, project mapping, utilization "
        "analytics, new-joiner allocation and natural-language queries for ~5,000 employees."
    ),
    version="1.0.0",
)

# CORS — allow the frontend dev server and any deployed origin.
origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
app.include_router(projects.router)
app.include_router(seats.router)
app.include_router(allocations.router)
app.include_router(dashboard.router)
app.include_router(assistant.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "Seat Allocation & Project Mapping API",
        "status": "ok",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
