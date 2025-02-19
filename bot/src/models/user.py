from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    money: Mapped[float] = mapped_column(Float, default=0.0)
    reg_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.utcnow
    )
    proxy_count: Mapped[int] = mapped_column(BigInteger, default=0)
