from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text, Numeric, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(128), nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    otp_code = Column(String(16), nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customers = relationship("Customer", back_populates="added_by")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    # Applicant details
    full_name = Column(String(255))
    father_spouse_name = Column(String(255))
    date_of_birth = Column(String(32))
    gender = Column(String(16))
    nationality = Column(String(64))
    marital_status = Column(String(32))
    occupation = Column(String(128))
    annual_income = Column(String(32))

    # Contact & address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(128))
    state = Column(String(128))
    pin_code = Column(String(16))
    mobile_number = Column(String(32))
    email = Column(String(128))

    # Identification
    aadhaar_id_number = Column(String(32))
    pan_number = Column(String(32))
    id_proof_type = Column(String(64))

    # Account details
    account_type = Column(String(16))  # savings / current
    initial_deposit = Column(String(32))

    # Nominee
    nominee_name = Column(String(255))
    nominee_relationship = Column(String(128))

    # Branch / declaration extras captured from the form
    branch = Column(String(128))
    form_date = Column(String(32))
    place = Column(String(128))
    signature_date = Column(String(32))

    form_image_path = Column(String(512))
    signature_image_path = Column(String(512))
    added_by_employee_id = Column(Integer, ForeignKey("employees.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    extraction_confidence = Column(Text)  # JSON string: { field: confidence }

    added_by = relationship("Employee", back_populates="customers")
