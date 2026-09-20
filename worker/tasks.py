from celery_app import app

from shared.db.session import SessionLocal

from shared.models.user import User
from shared.models.category import Category
from shared.models.supplier import Supplier
from shared.models.invoice import Invoice

from services.pdf_extractor import extract_pdf
from services.ai_pipeline import extract_fields
from services.validator import validate

def get_or_create_supplier(db, name: str) -> Supplier:
    normalized = name.strip().lower()

    supplier = (
        db.query(Supplier)
        .filter(Supplier.normalized_name == normalized)
        .first()
    )

    if supplier:
        return supplier

    supplier = Supplier(name=name, normalized_name=normalized)

    db.add(supplier)
    db.flush()

    return supplier


def get_or_create_category(db, name: str) -> Category:
    category = (
        db.query(Category)
        .filter(Category.name.ilike(name))
        .first()
    )

    if category:
        return category

    category = Category(name=name)

    db.add(category)
    db.flush()

    return category


@app.task
def process_invoice(invoice_id: int):
    db = SessionLocal()

    try:
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

        if invoice is None:
            return

        invoice_text = extract_pdf(invoice.file_path)
        result = extract_fields(invoice_text)

        if result is None:
            invoice.status = "review_required"
            invoice.review_reason = "AI extraction failed"
            db.commit()
            return

        invoice.raw_extracted_json = result.model_dump_json()

        if result.supplier_name:
            supplier = get_or_create_supplier(db, result.supplier_name)
            invoice.supplier_id = supplier.id

        if result.category:
            category = get_or_create_category(db, result.category)
            invoice.category_id = category.id


        invoice.invoice_date = result.invoice_date
        invoice.due_date = result.due_date
        invoice.net_amount = result.net_amount
        invoice.vat_amount = result.vat_amount
        invoice.gross_amount = result.gross_amount
        invoice.confidence_score = result.confidence_score

        validation = validate(result)
        invoice.status = validation.status
        invoice.review_reason = validation.reason

        db.commit()

    finally:
        db.close()