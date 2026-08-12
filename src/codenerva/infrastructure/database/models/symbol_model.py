from uuid import UUID

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from codenerva.infrastructure.database.base import Base


class SymbolModel(Base):
    __tablename__ = "symbols"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
    )

    source_file_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    qualified_name: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    kind: Mapped[str] = mapped_column(
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

    parent_symbol_id: Mapped[UUID | None] = mapped_column(
        nullable=True,
        index=True,
    )
