from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shared.db.session import get_db
from shared.models.user import User
from shared.models.invoice import Invoice
from shared.models.category import Category
from shared.models.supplier import Supplier

from app.core.security import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def get_dashboard_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    base = db.query(Invoice).filter(Invoice.user_id == current_user.id)

    return {
        "total": base.count(),
        "pending_review": base.filter(Invoice.status == "review_required").count(),
        "processing": base.filter(Invoice.status == "processing").count(),
        "ready_for_approval": base.filter(Invoice.status == "ready_for_approval").count(),
        "approved": base.filter(Invoice.status == "approved").count(),
    }