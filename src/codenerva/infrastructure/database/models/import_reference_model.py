from uuid import UUID

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from codenerva.infrastructure.database.base import Base


class ImportReferenceModel(Base):
    __tablename__ = "import_references"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
    )

    source_file_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    module: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    imported_name: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    alias: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    line: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
