from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import DATABASE_URL

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations():
    """Lightweight additive migration for SQLite: add any columns that
    exist on the models but not yet in an already-created table, so
    pre-existing local data survives schema changes across sessions."""
    with engine.connect() as conn:
        existing_cols = {
            row[1] for row in conn.execute(text("PRAGMA table_info(employees)"))
        }
        if existing_cols:
            additions = {
                "email": "ALTER TABLE employees ADD COLUMN email VARCHAR(128)",
                "is_verified": "ALTER TABLE employees ADD COLUMN is_verified BOOLEAN DEFAULT 0",
                "otp_code": "ALTER TABLE employees ADD COLUMN otp_code VARCHAR(16)",
                "otp_expires_at": "ALTER TABLE employees ADD COLUMN otp_expires_at DATETIME",
            }
            added_any = False
            for col, ddl in additions.items():
                if col not in existing_cols:
                    conn.execute(text(ddl))
                    added_any = True
            conn.commit()

            if added_any:
                # Pre-existing employees (created before verification existed)
                # should not be locked out.
                conn.execute(text("UPDATE employees SET is_verified = 1 WHERE is_verified IS NULL OR is_verified = 0"))
                conn.commit()

        existing_customer_cols = {
            row[1] for row in conn.execute(text("PRAGMA table_info(customers)"))
        }
        if existing_customer_cols:
            customer_additions = {
                "signature_image_path": "ALTER TABLE customers ADD COLUMN signature_image_path VARCHAR(512)",
                "signature_date": "ALTER TABLE customers ADD COLUMN signature_date VARCHAR(32)",
            }
            for col, ddl in customer_additions.items():
                if col not in existing_customer_cols:
                    conn.execute(text(ddl))
            conn.commit()
