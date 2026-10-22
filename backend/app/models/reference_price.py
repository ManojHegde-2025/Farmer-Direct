"""Reference price model."""

import enum
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import String, Enum, DateTime, ForeignKey, Numeric, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.commodity import CommodityUnit


class PriceClassification(str, enum.Enum):
    LIVE_EXTERNAL_SOURCE = "LIVE_EXTERNAL_SOURCE"
    OFFICIAL_PUBLISHED_DATA = "OFFICIAL_PUBLISHED_DATA"
    HISTORICAL_REFERENCE = "HISTORICAL_REFERENCE"
    DEMO_DATA = "DEMO_DATA"
    USER_REPORTED = "USER_REPORTED"


class ReferencePrice(Base):
    __tablename__ = "reference_prices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    commodity_id: Mapped[int] = mapped_column(
        ForeignKey("commodities.id"), nullable=False, index=True
    )
    variety: Mapped[str | None] = mapped_column(String(100), nullable=True)
    market: Mapped[str | None] = mapped_column(String(200), nullable=True)
    locality: Mapped[str | None] = mapped_column(String(200), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unit: Mapped[CommodityUnit] = mapped_column(Enum(CommodityUnit), nullable=False)
    observation_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    classification: Mapped[PriceClassification] = mapped_column(
        Enum(PriceClassification), default=PriceClassification.DEMO_DATA, nullable=False
    )
    quality_grade: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    commodity: Mapped["Commodity"] = relationship("Commodity", lazy="selectin")
