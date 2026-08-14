import os
from pathlib import Path

from qdrant_client import QdrantClient

from codenerva.application.analysis.codenerva_analysis_pipeline import (
    CodeNervaAnalysisPipeline,
)
from codenerva.application.analysis.run_analysis_job import (
    RunAnalysisJobUseCase,
)
from codenerva.application.analysis.start_analysis_job import (
    StartAnalysisJobUseCase,
)
from codenerva.infrastructure.database.postgres_analysis_job_store import (
    PostgresAnalysisJobStore,
)
from codenerva.infrastructure.database.postgres_chunk_store import (
    PostgresChunkStore,
)
from codenerva.infrastructure.database.postgres_import_reference_store import (
    PostgresImportReferenceStore,
)
from codenerva.infrastructure.database.postgres_project_repository import (
    PostgresProjectRepository,
)
from codenerva.infrastructure.database.postgres_repository_store import (
    PostgresRepositoryStore,
)
from codenerva.infrastructure.database.postgres_snapshot_store import (
    PostgresSnapshotStore,
)
from codenerva.infrastructure.database.postgres_source_file_relation_store import (
    PostgresSourceFileRelationStore,
)
from codenerva.infrastructure.database.postgres_source_file_store import (
    PostgresSourceFileStore,
)
from codenerva.infrastructure.database.postgres_symbol_relation_store import (
    PostgresSymbolRelationStore,
)
from codenerva.infrastructure.database.postgres_symbol_store import (
    PostgresSymbolStore,
)
from codenerva.infrastructure.database.session import (
    create_session_factory,
)
from codenerva.infrastructure.qdrant_vector_store import (
    QdrantVectorStore,
)
from codenerva.infrastructure.subprocess_git_client import (
    SubprocessGitClient,
)

storage_root = Path("storage")
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is not configured.")

session_factory = create_session_factory(
    database_url=database_url,
)

project_repository = PostgresProjectRepository(
    session_factory=session_factory,
)

repository_store = PostgresRepositoryStore(
    session_factory=session_factory,
)

snapshot_store = PostgresSnapshotStore(
    session_factory=session_factory,
)
analysis_job_store = PostgresAnalysisJobStore(
    session_factory=session_factory,
)
git_client = SubprocessGitClient()
source_file_store = PostgresSourceFileStore(
    session_factory=session_factory,
)
symbol_store = PostgresSymbolStore(
    session_factory=session_factory,
)
symbol_relation_store = PostgresSymbolRelationStore(
    session_factory=session_factory,
)
import_reference_store = PostgresImportReferenceStore(
    session_factory=session_factory,
)
source_file_relation_store = PostgresSourceFileRelationStore(
    session_factory=session_factory,
)
chunk_store = PostgresChunkStore(
    session_factory=session_factory,
)


qdrant_client = QdrantClient(path=str(storage_root / "qdrant"))

vector_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name="codenerva_chunks",
    dimensions=1536,
)


def get_codenerva_analysis_pipeline() -> CodeNervaAnalysisPipeline:
    from codenerva.api.snapshots import (
        get_analyze_snapshot_use_case,
        get_discover_snapshot_files_use_case,
        get_incremental_index_snapshot_use_case,
        get_index_snapshot_use_case,
    )

    return CodeNervaAnalysisPipeline(
        snapshot_store=snapshot_store,
        discover_snapshot_files_use_case=(get_discover_snapshot_files_use_case()),
        analyze_snapshot_use_case=(get_analyze_snapshot_use_case()),
        index_snapshot_use_case=(get_index_snapshot_use_case()),
        incremental_index_snapshot_use_case=(get_incremental_index_snapshot_use_case()),
    )


def get_start_analysis_job_use_case() -> StartAnalysisJobUseCase:
    return StartAnalysisJobUseCase(
        snapshot_store=snapshot_store,
        analysis_job_store=analysis_job_store,
    )


def get_run_analysis_job_use_case() -> RunAnalysisJobUseCase:
    return RunAnalysisJobUseCase(
        analysis_job_store=analysis_job_store,
        analysis_pipeline=get_codenerva_analysis_pipeline(),
        snapshot_store=snapshot_store,
    )
