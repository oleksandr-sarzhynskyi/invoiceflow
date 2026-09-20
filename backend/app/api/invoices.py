import uuid

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pathlib import Path
from typing import List, Optional
from datetime import datetime, date

from shared.db.session import get_db
from shared.models.user import User
from shared.models.invoice import Invoice
from shared.models.category import Category
from shared.models.supplier import Supplier

from app.core.security import get_current_user
from app.core.celery_client import app

UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter(prefix="/invoices", tags=["invoices"])


class InvoiceSummary(BaseModel):
    id: int
    original_filename: str
    status: str
    gross_amount: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceDetail(BaseModel):
    id: int
    original_filename: str
    status: str
    supplier_id: Optional[int]
    category_id: Optional[int]
    invoice_date: Optional[date]
    due_date: Optional[date]
    net_amount: Optional[float]
    vat_amount: Optional[float]
    gross_amount: Optional[float]
    confidence_score: Optional[float]
    review_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceUpdate(BaseModel):
    supplier_id: Optional[int] = None
    category_id: Optional[int] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    net_amount: Optional[float] = None
    vat_amount: Optional[float] = None
    gross_amount: Optional[float] = None


def get_display_filename(db: Session, user_id: int, filename: str) -> str:
    stem = Path(filename).stem
    suffix = Path(filename).suffix

    existing_names = {
        row[0]
        for row in db.query(Invoice.original_filename)
        .filter(Invoice.user_id == user_id)
        .all()
    }

    if filename not in existing_names:
        return filename

    n = 2
    while f"{stem} ({n}){suffix}" in existing_names:
        n += 1
    return f"{stem} ({n}){suffix}"


def get_owned_invoice(invoice_id: int, current_user: User, db: Session) -> Invoice:
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    return invoice


@router.post("/upload")
async def upload_invoice(
    file: UploadFile = File(description="Invoice to upload"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf" or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pdf files are allowed")

    safe_name = Path(file.filename).name
    unique_filename = f"{uuid.uuid4()}_{safe_name}"
    file_path = UPLOAD_DIR / unique_filename

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    display_filename = get_display_filename(db, current_user.id, file.filename)

    invoice = Invoice(
        user_id=current_user.id,
        original_filename=display_filename,
        file_path=str(file_path),
        status="processing",
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    app.send_task("tasks.process_invoice", args=[invoice.id])

    return {
        "id": invoice.id,
        "original_filename": invoice.original_filename,
        "status": invoice.status,
    }


@router.get("/", response_model=List[InvoiceSummary])
def list_invoices(status: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Invoice).filter(Invoice.user_id == current_user.id)

    if status:
        query = query.filter(Invoice.status == status)

    return query.order_by(Invoice.created_at.desc()).all()


@router.get("/{invoice_id}", response_model=InvoiceDetail)
def get_invoice(invoice_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoice = get_owned_invoice(invoice_id, current_user, db)

    return invoice


@router.patch("/{invoice_id}", response_model=InvoiceDetail)
def patch_invoice(
    invoice_id: int, 
    payload: InvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    invoice = get_owned_invoice(invoice_id, current_user, db)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(invoice, field, value)

    db.commit()
    db.refresh(invoice)

    return invoice


@router.post("/{invoice_id}/approve", response_model=InvoiceDetail)
def approve_invoice(invoice_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoice = get_owned_invoice(invoice_id, current_user, db)

    if invoice.status == "processing":
        raise HTTPException(
            status_code=400,
            detail="Invoice is still processing and cannot be approved yet",
        )

    if invoice.status == "approved":
        raise HTTPException(
            status_code=400,
            detail="Invoice is already approved",
        )

    invoice.status = "approved"

    db.commit()
    db.refresh(invoice)

    return invoice


@router.get("/{invoice_id}/file")
def get_invoice_file(invoice_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoice = get_owned_invoice(invoice_id, current_user, db)

    return FileResponse(
        invoice.file_path,
        media_type="application/pdf",
        filename=invoice.original_filename,
    )


@router.delete("/{invoice_id}")
def delete_invoice(invoice_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    invoice = get_owned_invoice(invoice_id, current_user, db)

    file_path = Path(invoice.file_path)
    if file_path.exists():
        file_path.unlink()

    db.delete(invoice)
    db.commit()

    return {"detail": "Invoice deleted"}