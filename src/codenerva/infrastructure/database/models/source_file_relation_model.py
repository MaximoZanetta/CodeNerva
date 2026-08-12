from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from codenerva.infrastructure.database.base import Base


class SourceFileRelationModel(Base):
    __tablename__ = "source_file_relations"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
    )

    source_file_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    target_file_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    kind: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
