from uuid import UUID

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from codenerva.infrastructure.database.base import Base


class ChunkModel(Base):
    __tablename__ = "chunks"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
    )

    snapshot_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    source_file_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    symbol_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    kind: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    relative_path: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    qualified_name: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    symbol_kind: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    start_line: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    end_line: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    part_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    part_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
