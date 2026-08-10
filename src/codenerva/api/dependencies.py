from pathlib import Path

from codenerva.infrastructure.in_memory_import_reference_store import (
    InMemoryImportReferenceStore,
)
from codenerva.infrastructure.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from codenerva.infrastructure.in_memory_repository_store import (
    InMemoryRepositoryStore,
)
from codenerva.infrastructure.in_memory_snapshot_store import (
    InMemorySnapshotStore,
)
from codenerva.infrastructure.in_memory_source_file_relation_store import (
    InMemorySourceFileRelationStore,
)
from codenerva.infrastructure.in_memory_source_file_store import (
    InMemorySourceFileStore,
)
from codenerva.infrastructure.in_memory_symbol_relation_store import (
    InMemorySymbolRelationStore,
)
from codenerva.infrastructure.in_memory_symbol_store import (
    InMemorySymbolStore,
)
from codenerva.infrastructure.subprocess_git_client import (
    SubprocessGitClient,
)

storage_root = Path("storage")

project_repository = InMemoryProjectRepository()
repository_store = InMemoryRepositoryStore()
snapshot_store = InMemorySnapshotStore()
git_client = SubprocessGitClient()
source_file_store = InMemorySourceFileStore()
symbol_store = InMemorySymbolStore()
symbol_relation_store = InMemorySymbolRelationStore()
import_reference_store = InMemoryImportReferenceStore()
source_file_relation_store = InMemorySourceFileRelationStore()
