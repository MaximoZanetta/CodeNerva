from sqlalchemy import Engine

from codenerva.infrastructure.database.base import Base
from codenerva.infrastructure.database.models.chunk_model import (
    ChunkModel,
)
from codenerva.infrastructure.database.models.import_reference_model import (
    ImportReferenceModel,
)
from codenerva.infrastructure.database.models.project_model import (
    ProjectModel,
)
from codenerva.infrastructure.database.models.repository_model import (
    RepositoryModel,
)
from codenerva.infrastructure.database.models.snapshot_model import (
    SnapshotModel,
)
from codenerva.infrastructure.database.models.source_file_model import (
    SourceFileModel,
)
from codenerva.infrastructure.database.models.source_file_relation_model import (
    SourceFileRelationModel,
)
from codenerva.infrastructure.database.models.symbol_model import (
    SymbolModel,
)
from codenerva.infrastructure.database.models.symbol_relation_model import (
    SymbolRelationModel,
)


def create_schema(
    *,
    engine: Engine,
) -> None:
    _ = (
        ProjectModel,
        RepositoryModel,
        SnapshotModel,
        SourceFileModel,
        SymbolModel,
        ImportReferenceModel,
        SourceFileRelationModel,
        SymbolRelationModel,
        ChunkModel,
    )

    Base.metadata.create_all(
        bind=engine,
    )
