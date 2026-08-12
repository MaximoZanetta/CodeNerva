from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from codenerva.infrastructure.database.base import Base


class SymbolRelationModel(Base):
    __tablename__ = "symbol_relations"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
    )

    source_symbol_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    target_symbol_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    kind: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
