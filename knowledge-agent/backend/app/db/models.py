"""
Database models — KnowledgeItem and AuditLog tables.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text, text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class KnowledgeItem(Base):
    """Structured knowledge entries loaded from JSON/CSV sources."""

    __tablename__ = "knowledge_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Origin format: json, csv, manual",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Full text content of the knowledge item",
    )
    content_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        comment="SHA-256 hash for deduplication",
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
        comment="Arbitrary metadata (category, price, specs, etc.)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<KnowledgeItem {self.id} source={self.source_type}>"


class AuditLog(Base):
    """Audit trail for every agent execution."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="User's original query",
    )
    reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Agent's reasoning over retrieved data",
    )
    chosen_action: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Action the agent decided to take",
    )
    result: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Output of the executed action",
    )
    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Human-readable explanation of the decision",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.id} action={self.chosen_action}>"
