from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from shared.db.session import get_db
from shared.models.user import User
from shared.models.invoice import Invoice
from shared.models.supplier import Supplier

from app.core.security import get_current_user

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

class SupplierStats(BaseModel):
    id: int
    name: str
    invoice_count: int
    total_spend: Optional[float]

    class Config:
        from_attributes: True


@router.get("/", response_model=List[SupplierStats])
def list_supplier_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = (
        db.query(
            Supplier.id,
            Supplier.name,
            func.count(Invoice.id).label("invoice_count"),
            func.sum(Invoice.gross_amount).label("total_spend"),
        )
        .join(Invoice, Invoice.supplier_id == Supplier.id)
        .filter(Invoice.user_id == current_user.id)
        .group_by(Supplier.id, Supplier.name)
        .order_by(func.sum(Invoice.gross_amount).desc())
        .all()
    )

    return [
        SupplierStats(
            id=row.id,
            name=row.name,
            invoice_count=row.invoice_count,
            total_spend=float(row.total_spend) if row.total_spend is not None else None,
        )
        for row in results
    ]