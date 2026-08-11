import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/customers", tags=["customers"])


def _to_out(c: models.Customer) -> schemas.CustomerOut:
    data = {col.name: getattr(c, col.name) for col in models.Customer.__table__.columns}
    data["added_by_name"] = c.added_by.full_name if c.added_by else None
    data["extraction_confidence"] = (
        json.loads(c.extraction_confidence) if c.extraction_confidence else None
    )
    return schemas.CustomerOut(**data)


@router.get("", response_model=schemas.CustomerListResponse)
def list_customers(
    search: str = Query("", description="Search by name, mobile, or city"),
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc"),
    account_type: str = Query(""),
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(auth.get_current_employee),
):
    q = db.query(models.Customer)
    if search:
        like = f"%{search}%"
        q = q.filter(
            or_(
                models.Customer.full_name.ilike(like),
                models.Customer.mobile_number.ilike(like),
                models.Customer.city.ilike(like),
                models.Customer.email.ilike(like),
            )
        )
    if account_type:
        q = q.filter(models.Customer.account_type == account_type)

    sort_col = getattr(models.Customer, sort_by, models.Customer.created_at)
    q = q.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())

    total = q.count()
    items = q.all()

    all_customers = db.query(models.Customer).all()
    today = datetime.now(timezone.utc).date()
    added_today = sum(
        1 for c in all_customers
        if c.created_at and c.created_at.date() == today
    )
    savings = sum(1 for c in all_customers if c.account_type == "savings")
    current = sum(1 for c in all_customers if c.account_type == "current")

    stats = {
        "total_customers": len(all_customers),
        "added_today": added_today,
        "savings_accounts": savings,
        "current_accounts": current,
    }

    return schemas.CustomerListResponse(
        items=[schemas.CustomerListItem.model_validate(c) for c in items],
        total=total,
        stats=stats,
    )


@router.get("/{customer_id}", response_model=schemas.CustomerOut)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(auth.get_current_employee),
):
    c = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
    return _to_out(c)


@router.post("", response_model=schemas.CustomerOut)
def create_customer(
    payload: schemas.CustomerCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(auth.get_current_employee),
):
    data = payload.model_dump(exclude={"extraction_confidence"})
    c = models.Customer(**data, added_by_employee_id=current_employee.id)
    if payload.extraction_confidence is not None:
        c.extraction_confidence = json.dumps(payload.extraction_confidence)
    db.add(c)
    db.commit()
    db.refresh(c)
    return _to_out(c)


@router.put("/{customer_id}", response_model=schemas.CustomerOut)
def update_customer(
    customer_id: int,
    payload: schemas.CustomerUpdate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(auth.get_current_employee),
):
    c = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    db.commit()
    db.refresh(c)
    return _to_out(c)


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(auth.get_current_employee),
):
    c = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(c)
    db.commit()
    return {"ok": True}
