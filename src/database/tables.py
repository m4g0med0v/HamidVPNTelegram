from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    create_date = Column(DateTime, default=func.now(), nullable=False)
    money = Column(Float, default=0.0, nullable=False)
    count_proxies = Column(Integer, default=0, nullable=False)

    proxies = relationship(
        "Proxy", back_populates="user", cascade="all, delete-orphan"
    )


class Proxy(Base):
    __tablename__ = "proxies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger, ForeignKey("users.id"), nullable=False, index=True
    )
    ip = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    vless_id = Column(String, nullable=False, unique=True)
    private_key = Column(String, nullable=False, unique=True)
    public_key = Column(String, nullable=False, unique=True)
    short_id = Column(String, nullable=False, unique=True)
    link = Column(String, nullable=False)
    is_freezed = Column(Boolean, default=False)

    user = relationship("User", back_populates="proxies")


class Journal(Base):
    __tablename__ = "journal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    action = Column(
        Enum("create", "delete", name="action_types"),
        nullable=False,
    )
    proxy_id = Column(String, nullable=True)
    date = Column(DateTime, default=func.now(), nullable=False)
