from uuid import UUID

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from codenerva.infrastructure.database.base import Base


class SourceFileModel(Base):
    __tablename__ = "source_files"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
    )

    snapshot_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    relative_path: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
