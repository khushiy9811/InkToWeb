"""Seed a default employee login for local/demo use."""
from app.database import SessionLocal, Base, engine, run_migrations
from app import models, auth

run_migrations()
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    existing = db.query(models.Employee).filter(
        models.Employee.username == "admin"
    ).first()
    if existing:
        print("Default employee 'admin' already exists.")
    else:
        employee = models.Employee(
            username="admin",
            email="admin@inktoweb.local",
            password_hash=auth.hash_password("admin123"),
            full_name="Bank Administrator",
            is_verified=True,
        )
        db.add(employee)
        db.commit()
        print("Seeded default employee -> username: admin / password: admin123")
finally:
    db.close()
