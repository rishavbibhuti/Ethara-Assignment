"""Seed data generator.

Creates a realistic dataset:
  * ~5,600 seats across 4 buildings x 5 floors x 4 zones
  * ~40 projects across departments
  * 5,000 employees (mix of active, new joiners, inactive)
  * ~88% of employees allocated a seat, with matching allocation history

Run with:  python -m app.seed         (from the backend/ directory)
Add --reset to drop and recreate all tables first.
"""
import random
import sys
from datetime import date, datetime, timedelta

from faker import Faker

from .database import Base, SessionLocal, engine
from . import models

fake = Faker()
Faker.seed(42)
random.seed(42)

BUILDINGS = ["Building A", "Building B", "Building C", "Building D"]
FLOORS = ["1", "2", "3", "4", "5"]
ZONES = ["North", "South", "East", "West"]
SEATS_PER_ZONE = 70  # 4 * 5 * 4 * 70 = 5,600 seats

DEPARTMENTS = [
    "Engineering", "Data", "Design", "Product", "Quality Assurance",
    "HR", "Finance", "Sales", "Marketing", "Operations", "IT", "Legal",
]
DESIGNATIONS = [
    "Associate", "Software Engineer", "Senior Engineer", "Lead", "Manager",
    "Architect", "Analyst", "Senior Analyst", "Director", "Intern",
]
TEAMS = [
    "Platform", "Payments", "Mobile", "Web", "Infra", "ML", "Analytics",
    "Growth", "Support", "Security", "DevOps", "Core",
]
PROJECT_NAMES = [
    "Data Platform", "Customer 360", "Mobile Revamp", "Payment Gateway",
    "Cloud Migration", "Analytics Hub", "Security Overhaul", "HR Portal",
    "Finance Automation", "Marketing Suite", "Sales CRM", "Support Desk",
    "Inventory System", "Recommendation Engine", "Fraud Detection",
    "Onboarding Flow", "Billing Engine", "Notification Service",
    "Search Revamp", "Loyalty Program", "Partner API", "Internal Tools",
    "Compliance Tracker", "Data Warehouse", "Reporting Suite", "Chatbot",
    "Identity Service", "Feature Flags", "A/B Testing", "Cost Optimizer",
    "Green Field", "Legacy Sunset", "Edge Delivery", "Video Pipeline",
    "IoT Gateway", "Voice Assistant", "AR Try-On", "Marketplace",
    "Subscription Manager", "Audit Trail",
]


def reset_db():
    print("Dropping and recreating all tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.Employee).count() > 0:
            print("Database already has data. Use `python -m app.seed --reset` to reseed.")
            return

        # ---- Seats ----
        print("Creating seats...")
        seat_rows = []
        for b in BUILDINGS:
            for f in FLOORS:
                for z in ZONES:
                    for n in range(1, SEATS_PER_ZONE + 1):
                        bcode = b.split()[-1]  # A/B/C/D
                        seat_rows.append(
                            {
                                "seat_number": f"{bcode}{f}-{z[0]}{n:03d}",
                                "building": b,
                                "floor": f,
                                "zone": z,
                                "seat_type": random.choices(
                                    ["desk", "hot_desk", "cabin"], weights=[85, 10, 5]
                                )[0],
                                "status": "available",
                            }
                        )
        db.bulk_insert_mappings(models.Seat, seat_rows)
        db.commit()
        seat_ids = [r[0] for r in db.query(models.Seat.id).all()]
        print(f"  -> {len(seat_ids)} seats")

        # ---- Projects ----
        print("Creating projects...")
        project_rows = []
        for i, name in enumerate(PROJECT_NAMES, start=1):
            start = fake.date_between(start_date="-3y", end_date="-1M")
            project_rows.append(
                {
                    "code": f"PRJ-{i:03d}",
                    "name": name,
                    "department": random.choice(DEPARTMENTS),
                    "manager": fake.name(),
                    "status": random.choices(
                        ["active", "on_hold", "completed"], weights=[75, 15, 10]
                    )[0],
                    "start_date": start,
                    "end_date": None,
                    "description": fake.sentence(nb_words=10),
                }
            )
        db.bulk_insert_mappings(models.Project, project_rows)
        db.commit()
        project_ids = [r[0] for r in db.query(models.Project.id).all()]
        print(f"  -> {len(project_ids)} projects")

        # ---- Employees ----
        print("Creating 5,000 employees...")
        random.shuffle(seat_ids)
        seat_pool = list(seat_ids)  # seats we can hand out
        occupied_seat_ids = []
        history_rows = []
        employee_rows = []
        used_emails = set()

        TOTAL = 5000
        for i in range(1, TOTAL + 1):
            status = random.choices(
                ["active", "new_joiner", "inactive"], weights=[85, 10, 5]
            )[0]
            first, last = fake.first_name(), fake.last_name()
            email = f"{first.lower()}.{last.lower()}{i}@company.com"
            join_date = (
                fake.date_between(start_date="-15d", end_date="today")
                if status == "new_joiner"
                else fake.date_between(start_date="-6y", end_date="-1M")
            )

            # Seat allocation policy:
            #   active     -> ~95% seated
            #   new_joiner -> ~40% seated (rest await allocation)
            #   inactive   -> never seated
            seat_id = None
            if status == "active" and random.random() < 0.95 and seat_pool:
                seat_id = seat_pool.pop()
            elif status == "new_joiner" and random.random() < 0.40 and seat_pool:
                seat_id = seat_pool.pop()

            emp_id = i  # matches autoincrement on a fresh DB
            if seat_id:
                occupied_seat_ids.append(seat_id)
                history_rows.append(
                    {
                        "employee_id": emp_id,
                        "seat_id": seat_id,
                        "action": "allocated",
                        "allocated_by": "seed",
                        "timestamp": datetime.utcnow() - timedelta(days=random.randint(0, 400)),
                        "note": "Initial allocation",
                    }
                )

            employee_rows.append(
                {
                    "employee_code": f"EMP{i:05d}",
                    "name": f"{first} {last}",
                    "email": email,
                    "designation": random.choice(DESIGNATIONS),
                    "department": random.choice(DEPARTMENTS),
                    "team": random.choice(TEAMS),
                    "status": status,
                    "join_date": join_date,
                    "project_id": random.choice(project_ids) if random.random() < 0.9 else None,
                    "seat_id": seat_id,
                }
            )

        db.bulk_insert_mappings(models.Employee, employee_rows)
        db.commit()
        print(f"  -> {len(employee_rows)} employees ({len(occupied_seat_ids)} seated)")

        # ---- Mark occupied seats ----
        print("Updating seat occupancy...")
        if occupied_seat_ids:
            CHUNK = 900  # stay under SQLite's parameter limit
            for start in range(0, len(occupied_seat_ids), CHUNK):
                chunk = occupied_seat_ids[start : start + CHUNK]
                db.query(models.Seat).filter(models.Seat.id.in_(chunk)).update(
                    {models.Seat.status: "occupied"}, synchronize_session=False
                )
            db.commit()

        # A few reserved / maintenance seats for realism.
        spare = [s for s in seat_pool[:60]]
        if spare:
            half = len(spare) // 2
            db.query(models.Seat).filter(models.Seat.id.in_(spare[:half])).update(
                {models.Seat.status: "reserved"}, synchronize_session=False
            )
            db.query(models.Seat).filter(models.Seat.id.in_(spare[half:])).update(
                {models.Seat.status: "maintenance"}, synchronize_session=False
            )
            db.commit()

        # ---- Allocation history ----
        print("Writing allocation history...")
        if history_rows:
            db.bulk_insert_mappings(models.AllocationHistory, history_rows)
            db.commit()

        print("\nSeed complete.")
        print(f"  Employees : {db.query(models.Employee).count()}")
        print(f"  Projects  : {db.query(models.Project).count()}")
        print(f"  Seats     : {db.query(models.Seat).count()}")
        print(f"  Occupied  : {db.query(models.Seat).filter(models.Seat.status=='occupied').count()}")
        print(f"  Available : {db.query(models.Seat).filter(models.Seat.status=='available').count()}")
    finally:
        db.close()


if __name__ == "__main__":
    if "--reset" in sys.argv:
        reset_db()
    seed()
