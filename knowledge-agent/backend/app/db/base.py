"""
SQLAlchemy declarative base — all ORM models inherit from this.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass
