from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): ...


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    money: Mapped[float] = mapped_column(Float, default=0.0)
    reg_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.utcnow
    )
    proxy_count: Mapped[int] = mapped_column(BigInteger, default=0)


class Proxy(Base):
    __tablename__ = "proxies"

    uuid: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    short_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    create_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.utcnow
    )
    server_ip: Mapped[str] = mapped_column(String, nullable=False)
    link: Mapped[str] = mapped_column(String, nullable=False)
    is_freeze: Mapped[bool] = mapped_column(Boolean, default=False)


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


class Bank(Base):
    __tablename__ = "bank"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.utcnow
    )
    currency: Mapped[str] = mapped_column(String, default="RUB")
    amount: Mapped[float] = mapped_column(Float, nullable=False)
