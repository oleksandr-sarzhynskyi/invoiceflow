import logging

from google import genai
from pydantic import BaseModel
from typing import Optional

from config import API_KEY, MODEL

logger = logging.getLogger(__name__)

class ExtractedInvoice(BaseModel):
    supplier_name: Optional[str]
    invoice_date: Optional[str]
    due_date: Optional[str]
    net_amount: Optional[float]
    vat_amount: Optional[float]
    gross_amount: Optional[float]
    category: Optional[str]
    confidence_score: float

client = genai.Client(api_key=API_KEY)

PROMPT_TEMPLATE = """You are extracting structured data from an invoice.

Below is the raw text extracted from an invoice PDF. Read it carefully and extract the following fields:

- supplier_name: the name of the company that issued the invoice (not the recipient)
- invoice_date: the date the invoice was issued, in YYYY-MM-DD format
- due_date: the payment due date, in YYYY-MM-DD format
- net_amount: the subtotal before tax, as a plain number (no currency symbols, no commas)
- vat_amount: the tax/VAT amount, as a plain number
- gross_amount: the total amount including tax, as a plain number
- category: a short spending category for this invoice (e.g. "Software", "Office Supplies", "Travel", "Utilities", "Professional Services", "Other")
- confidence_score: your confidence in the overall extraction, from 0.0 to 1.0

Rules:
- If a field is not present in the text or you are not reasonably sure of its value, return null for that field. Do not guess or estimate a value.
- Dates must be in YYYY-MM-DD format. If the source date format is ambiguous, use your best judgment but lower the confidence_score accordingly.
- Amounts must be plain numbers (e.g. 1035.00), never strings, never including currency symbols.
- confidence_score should reflect the invoice as a whole — lower it if the text is garbled, incomplete, or if you had to infer several fields.

Respond with a JSON object matching exactly this shape, and nothing else.

Invoice text:
---
{invoice_text}
---
"""

def build_prompt(invoice_text: str) -> str:
    return PROMPT_TEMPLATE.format(invoice_text=invoice_text)

def extract_fields(invoice_text: str) -> Optional[ExtractedInvoice]:
    prompt = build_prompt(invoice_text)

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ExtractedInvoice,
            }
        )

        return response.parsed
    except Exception:
        logger.exception("Gemini extraction failed")
        return None