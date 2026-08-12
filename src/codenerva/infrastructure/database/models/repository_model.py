from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from codenerva.infrastructure.database.base import Base


class RepositoryModel(Base):
    __tablename__ = "repositories"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
    )

    project_id: Mapped[UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    remote_url: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    owner: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
