"""Commodity model."""

import enum
from datetime import datetime

from sqlalchemy import String, Boolean, Enum, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CommodityUnit(str, enum.Enum):
    KG = "KG"
    QUINTAL = "QUINTAL"
    TONNE = "TONNE"
    COUNT = "COUNT"
    BUNCH = "BUNCH"
    DOZEN = "DOZEN"


class Commodity(Base):
    __tablename__ = "commodities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name_kn: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    unit: Mapped[CommodityUnit] = mapped_column(Enum(CommodityUnit), nullable=False, default=CommodityUnit.KG)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
