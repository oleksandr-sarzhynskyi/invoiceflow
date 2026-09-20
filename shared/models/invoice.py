from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Date, DateTime, Numeric, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.models.base import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    original_filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))

    status: Mapped[str] = mapped_column(String(30), default="processing")

    supplier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id"), nullable=True)

    invoice_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    net_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    vat_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    gross_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)

    confidence_score: Mapped[Optional[float]] = mapped_column(nullable=True)
    review_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_extracted_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())