from pydantic import BaseModel
from typing import Optional

from services.ai_pipeline import ExtractedInvoice


class ValidationResult(BaseModel):
    status: str
    reason: Optional[str]


def validate(invoice: ExtractedInvoice) -> ValidationResult:
    errors = []

    required_fields = [
        "supplier_name",
        "invoice_date",
        "due_date",
        "net_amount",
        "vat_amount",
        "gross_amount",
    ]

    missing_fields = [
        field
        for field in required_fields
        if getattr(invoice, field) is None
    ]

    if missing_fields:
        errors.append(
            f"Missing fields: {', '.join(missing_fields)}"
        )

    if not missing_fields:
        if abs((invoice.net_amount + invoice.vat_amount)- invoice.gross_amount) > 0.01:
            errors.append("Math mismatch")

    if invoice.confidence_score <= 0.7:
        errors.append("Low confidence score")

    if errors:
        return ValidationResult(
            status="review_required",
            reason=", ".join(errors),
        )

    return ValidationResult(
        status="ready_for_approval",
        reason=None,
    )