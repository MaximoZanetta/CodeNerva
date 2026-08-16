const API_URL = "http://localhost:8000/api/v1"

export type Project = {
  id: string
  name: string
  description: string | null
  status: string
}

export type Repository = {
  id: string
  project_id: string
  remote_url: string
  owner: string
  name: string
  status: string
}

export type Snapshot = {
  id: string
  repository_id: string
  commit_sha: string
  branch: string | null
  remote_url: string
  status: string
}

export type AnalysisJob = {
  id: string
  snapshot_id: string
  status: string
  progress: number
  error_message: string | null
}

export type SourceFile = {
  id: string
  relative_path: string
  language: string
  size_bytes: number
  content_hash: string
}

export type Symbol = {
  id: string
  name: string
  qualified_name: string
  kind: string
  start_line: number
  end_line: number
  parent_symbol_id: string | null
}

export type ImportReference = {
  id: string
  module: string
  imported_name: string | null
  alias: string | null
  line: number
  resolved_source_file_id: string | null
  resolved_relative_path: string | null
}

export type SourceFileRelation = {
  id: string
  kind: string
  target_source_file_id: string
  target_relative_path: string
}

export type SymbolRelation = {
  id: string
  kind: string
  source_symbol_id: string
  source_symbol_name: string
  target_symbol_id: string
  target_symbol_name: string
}

type ListSnapshotsResponse = {
  snapshots: Snapshot[]
}

type ListSnapshotFilesResponse = {
  snapshot_id: string
  files: SourceFile[]
}

type ListSourceFileSymbolsResponse = {
  source_file_id: string
  symbols: Symbol[]
}

type ListSourceFileImportsResponse = {
  source_file_id: string
  imports: ImportReference[]
}

type ListSourceFileRelationsResponse = {
  source_file_id: string
  relations: SourceFileRelation[]
}

type ListSymbolRelationsResponse = {
  source_file_id: string
  relations: SymbolRelation[]
}
export type CallTraversalNode = {
  symbol_id: string
  symbol_name: string
  depth: number
}

export type CallTraversal = {
  root_symbol_id: string
  root_symbol_name: string
  nodes: CallTraversalNode[]
}

export type AskRepositorySource = {
  relative_path: string
  qualified_name: string
  symbol_kind: string
  language: string
  start_line: number
  end_line: number
  semantic_score: number | null
  semantic_rank: number | null
  graph_relations: string[]
  retrieval_origin: string
  final_score: number
}

export type RetrievalDiagnostics = {
  semantic_sources: number
  graph_sources: number
  both_sources: number
  final_context_items: number
}

export type AskRepositoryResponse = {
  snapshot_id: string
  question: string
  answer: string
  context_items: number
  sources: AskRepositorySource[]
  retrieval_diagnostics: RetrievalDiagnostics
}

async function readError(
  response: Response,
  fallback: string,
): Promise<string> {
  try {
    const payload: { detail?: string } =
      await response.json()

    return payload.detail ?? fallback
  } catch {
    return fallback
  }
}

export async function getProject(
  projectId: string,
): Promise<Project> {
  const response = await fetch(
    `${API_URL}/projects/${projectId}`,
  )

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        "Could not load project.",
      ),
    )
  }

  return response.json()
}

export async function getProjectRepository(
  projectId: string,
): Promise<Repository> {
  const response = await fetch(
    `${API_URL}/projects/${projectId}/repository`,
  )

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        "Could not load repository.",
      ),
    )
  }

  return response.json()
}

export async function listRepositorySnapshots(
  repositoryId: string,
): Promise<Snapshot[]> {
  const response = await fetch(
    `${API_URL}/repositories/${repositoryId}/snapshots`,
  )

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        "Could not load snapshots.",
      ),
    )
  }

  const payload: ListSnapshotsResponse =
    await response.json()

  return payload.snapshots
}

export async function listSnapshotFiles(
  snapshotId: string,
): Promise<SourceFile[]> {
  const response = await fetch(
    `${API_URL}/snapshots/${snapshotId}/files`,
  )

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        "Could not load snapshot files.",
      ),
    )
  }

  const payload: ListSnapshotFilesResponse =
    await response.json()

  return payload.files
}

export async function listSourceFileSymbols(
  sourceFileId: string,
): Promise<Symbol[]> {
  const response = await fetch(
    `${API_URL}/snapshots/files/${sourceFileId}/symbols`,
  )

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        "Could not load file symbols.",
      ),
    )
  }

  const payload: ListSourceFileSymbolsResponse =
    await response.json()

  return payload.symbols
}

export async function listSourceFileImports(
  sourceFileId: string,
): Promise<ImportReference[]> {
  const response = await fetch(
    `${API_URL}/snapshots/files/${sourceFileId}/imports`,
  )

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        "Could not load file imports.",
      ),
    )
  }

  const payload: ListSourceFileImportsResponse =
    await response.json()

  return payload.imports
}

export async function listSourceFileRelations(
  sourceFileId: string,
): Promise<SourceFileRelation[]> {
  const response = await fetch(
    `${API_URL}/snapshots/files/${sourceFileId}/relations`,
  )

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        "Could not load file relations.",
      ),
    )
  }

  const payload: ListSourceFileRelationsResponse =
    await response.json()

  return payload.relations
}

export async function listSymbolRelations(
  sourceFileId: string,
): Promise<SymbolRelation[]> {
  const response = await fetch(
    `${API_URL}/snapshots/files/${sourceFileId}/symbol-relations`,
  )

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        "Could not load symbol relations.",
      ),
    )
  }

  const payload: ListSymbolRelationsResponse =
    await response.json()

  return payload.relations
}

export async function cloneRepository(
  repositoryId: string,
): Promise<void> {
  const response = await fetch(
    `${API_URL}/repositories/${repositoryId}/clone`,
    {
      method: "POST",
    },
  )

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        "Could not clone repository.",
      ),
    )
  }
}

export async function createSnapshot(
  repositoryId: string,
): Promise<Snapshot> {
  const response = await fetch(
    `${API_URL}/repositories/${repositoryId}/snapshots`,
    {
      method: "POST",
    },
  )

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        "Could not create snapshot.",
      ),
    )
  }

  return response.json()
}

export async function startAnalysisJob(
  snapshotId: string,
): Promise<AnalysisJob> {
  const response = await fetch(
    `${API_URL}/analysis-jobs`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        snapshot_id: snapshotId,
      }),
    },
  )

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        "Could not start analysis.",
      ),
    )
  }

  return response.json()
}

export async function getAnalysisJob(
  jobId: string,
): Promise<AnalysisJob> {
  const response = await fetch(
    `${API_URL}/analysis-jobs/${jobId}`,
  )

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        "Could not load analysis job.",
      ),
    )
  }

  return response.json()
}

export async function getSymbolCalls(
  symbolId: string,
  maxDepth = 2,
): Promise<CallTraversal> {
  const response = await fetch(
    `${API_URL}/snapshots/symbols/${symbolId}/calls?max_depth=${maxDepth}`,
  )

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        "Could not load symbol call graph.",
      ),
    )
  }

  return response.json()
}

export async function askRepositoryQuestion(
  snapshotId: string,
  question: string,
): Promise<AskRepositoryResponse> {
  const response = await fetch(
    `${API_URL}/snapshots/ask`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        snapshot_id: snapshotId,
        question,
        top_k: 3,
        max_items: 6,
        max_chars: 12000,
      }),
    },
  )

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        "Could not answer repository question.",
      ),
    )
  }

  return response.json()
}