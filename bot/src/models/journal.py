from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Journal(Base):
    __tablename__ = "journal"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.utcnow
    )
    action: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
