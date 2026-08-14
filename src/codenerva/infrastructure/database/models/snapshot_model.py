from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from codenerva.infrastructure.database.base import Base


class SnapshotModel(Base):
    __tablename__ = "snapshots"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
    )

    repository_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    commit_sha: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    branch: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    remote_url: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
