from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, auth, email_service
from ..config import OTP_EXPIRE_MINUTES, EMAIL_DEV_MODE
from ..database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(
        models.Employee.username == payload.username
    ).first()
    if not employee or not auth.verify_password(payload.password, employee.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if not employee.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in.",
        )
    token = auth.create_access_token(employee.id, employee.username)
    return schemas.TokenResponse(access_token=token, employee=employee)


@router.get("/me", response_model=schemas.EmployeeOut)
def me(current_employee: models.Employee = Depends(auth.get_current_employee)):
    return current_employee


def _issue_otp(employee: models.Employee, db: Session) -> str:
    otp = auth.generate_otp()
    employee.otp_code = otp
    employee.otp_expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)
    db.commit()
    email_service.send_otp_email(employee.email, otp, employee.full_name)
    return otp


@router.post("/signup", response_model=schemas.SignupResponse)
def signup(payload: schemas.SignupRequest, db: Session = Depends(get_db)):
    username_taken = db.query(models.Employee).filter(
        models.Employee.username == payload.username
    ).first()
    if username_taken:
        raise HTTPException(status_code=400, detail="That username is already taken.")

    existing_email = db.query(models.Employee).filter(
        models.Employee.email == payload.email
    ).first()
    if existing_email and existing_email.is_verified:
        raise HTTPException(
            status_code=400, detail="An account with this email already exists."
        )

    if existing_email:
        # Re-signup before completing verification — refresh the pending record.
        employee = existing_email
        employee.username = payload.username
        employee.full_name = payload.full_name
        employee.password_hash = auth.hash_password(payload.password)
    else:
        employee = models.Employee(
            username=payload.username,
            email=payload.email,
            full_name=payload.full_name,
            password_hash=auth.hash_password(payload.password),
            is_verified=False,
        )
        db.add(employee)
    db.commit()
    db.refresh(employee)

    otp = _issue_otp(employee, db)

    return schemas.SignupResponse(
        message="Account created. Enter the code sent to your email to verify it.",
        email=employee.email,
        dev_otp=otp if EMAIL_DEV_MODE else None,
    )


@router.post("/resend-otp", response_model=schemas.SignupResponse)
def resend_otp(payload: schemas.ResendOtpRequest, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(
        models.Employee.email == payload.email
    ).first()
    if not employee or employee.is_verified:
        raise HTTPException(
            status_code=400, detail="No pending verification for this email."
        )

    otp = _issue_otp(employee, db)

    return schemas.SignupResponse(
        message="A new verification code has been sent.",
        email=employee.email,
        dev_otp=otp if EMAIL_DEV_MODE else None,
    )


@router.post("/verify-otp", response_model=schemas.TokenResponse)
def verify_otp(payload: schemas.VerifyOtpRequest, db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(
        models.Employee.email == payload.email
    ).first()
    if not employee or not employee.otp_code or employee.otp_code != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid verification code.")
    if not employee.otp_expires_at or employee.otp_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="This code has expired. Request a new one.",
        )

    employee.is_verified = True
    employee.otp_code = None
    employee.otp_expires_at = None
    db.commit()
    db.refresh(employee)

    token = auth.create_access_token(employee.id, employee.username)
    return schemas.TokenResponse(access_token=token, employee=employee)
