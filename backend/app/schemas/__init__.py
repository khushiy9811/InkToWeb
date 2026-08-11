from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------- Auth ----------

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    employee: "EmployeeOut"


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    full_name: str
    email: Optional[str] = None


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=6, max_length=128)


class SignupResponse(BaseModel):
    message: str
    email: str
    dev_otp: Optional[str] = None


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str


class ResendOtpRequest(BaseModel):
    email: EmailStr


# ---------- Customer field set (shared) ----------

CUSTOMER_FIELDS = [
    "full_name", "father_spouse_name", "date_of_birth", "gender",
    "nationality", "marital_status", "occupation", "annual_income",
    "address_line1", "address_line2", "city", "state", "pin_code",
    "mobile_number", "email",
    "aadhaar_id_number", "pan_number", "id_proof_type",
    "account_type", "initial_deposit",
    "nominee_name", "nominee_relationship",
    "branch", "form_date", "place", "signature_date",
]


class CustomerBase(BaseModel):
    full_name: Optional[str] = None
    father_spouse_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    marital_status: Optional[str] = None
    occupation: Optional[str] = None
    annual_income: Optional[str] = None

    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pin_code: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[str] = None

    aadhaar_id_number: Optional[str] = None
    pan_number: Optional[str] = None
    id_proof_type: Optional[str] = None

    account_type: Optional[str] = None
    initial_deposit: Optional[str] = None

    nominee_name: Optional[str] = None
    nominee_relationship: Optional[str] = None

    branch: Optional[str] = None
    form_date: Optional[str] = None
    place: Optional[str] = None
    signature_date: Optional[str] = None


class CustomerCreate(CustomerBase):
    form_image_path: Optional[str] = None
    signature_image_path: Optional[str] = None
    extraction_confidence: Optional[dict] = None


class CustomerUpdate(CustomerBase):
    pass


class CustomerOut(CustomerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    form_image_path: Optional[str] = None
    signature_image_path: Optional[str] = None
    added_by_employee_id: Optional[int] = None
    added_by_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    extraction_confidence: Optional[dict] = None


class CustomerListItem(BaseModel):
    id: int
    full_name: Optional[str] = None
    account_type: Optional[str] = None
    mobile_number: Optional[str] = None
    city: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CustomerListResponse(BaseModel):
    items: list[CustomerListItem]
    total: int
    stats: dict


# ---------- OCR extraction ----------

class ExtractedField(BaseModel):
    value: str
    confidence: float


class ExtractionResponse(BaseModel):
    fields: dict[str, ExtractedField]
    image_path: str
    signature_image_path: Optional[str] = None


TokenResponse.model_rebuild()
