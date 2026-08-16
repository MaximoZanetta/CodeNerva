import { useEffect, useMemo, useState } from "react"
import { useParams, useSearchParams } from "react-router-dom"
import FileInspector from "../components/repository/FileInspector"
import RepositoryFileTree from "../components/repository/RepositoryFileTree"
import {
  getProjectRepository,
  listRepositorySnapshots,
  listSnapshotFiles,
  listSourceFileImports,
  listSourceFileRelations,
  listSourceFileSymbols,
  listSymbolRelations,
  type ImportReference,
  type Repository,
  type Snapshot,
  type SourceFile,
  type SourceFileRelation,
  type Symbol,
  type SymbolRelation,
} from "../services/codenervaApi"
import CodeGraphPanel from "../components/repository/CodeGraphPanel"


function RepositoryPage() {
  const [searchParams] = useSearchParams()

  const requestedFile =
  searchParams.get("file")

  
  const { projectId } = useParams()
  const [selectedSymbol, setSelectedSymbol] = useState<Symbol | null>(null)
  const [repository, setRepository] =
    useState<Repository | null>(null)

  const [snapshot, setSnapshot] =
    useState<Snapshot | null>(null)

  const [files, setFiles] =
    useState<SourceFile[]>([])

  const [selectedFileId, setSelectedFileId] =
    useState<string | null>(null)

  const [symbols, setSymbols] =
    useState<Symbol[]>([])

  const [imports, setImports] =
    useState<ImportReference[]>([])

  const [fileRelations, setFileRelations] =
    useState<SourceFileRelation[]>([])

  const [symbolRelations, setSymbolRelations] =
    useState<SymbolRelation[]>([])

  const [loading, setLoading] = useState(true)
  const [detailsLoading, setDetailsLoading] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      return
    }

    const currentProjectId = projectId
    let cancelled = false

    async function loadRepository() {
      try {
        const loadedRepository =
          await getProjectRepository(currentProjectId)

        const snapshots =
          await listRepositorySnapshots(
            loadedRepository.id,
          )

        const readySnapshot =
          snapshots.find(
            (item) => item.status === "READY",
          ) ?? null

        if (!readySnapshot) {
          throw new Error(
            "This repository does not have a READY snapshot yet.",
          )
        }

        const loadedFiles =
          await listSnapshotFiles(
            readySnapshot.id,
          )

        if (cancelled) {
          return
        }

        setRepository(loadedRepository)
        setSnapshot(readySnapshot)
        setFiles(loadedFiles)

        if (loadedFiles.length > 0) {
            const requestedSourceFile =
                requestedFile
                ? loadedFiles.find(
                    (file) =>
                        file.relative_path ===
                        requestedFile,
                    )
                : null

            setSelectedFileId(
                requestedSourceFile?.id ??
                loadedFiles[0].id,
            )
            }

        setError(null)
      } catch (caughtError) {
        if (cancelled) {
          return
        }

        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Could not load repository.",
        )
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadRepository()

    return () => {
      cancelled = true
    }
  }, [projectId,requestedFile])

    useEffect(() => {
      if (!selectedFileId) {
        return
    }
    const currentFileId = selectedFileId
    let cancelled = false

    async function loadFileDetails() {
      setDetailsLoading(true)

      try {
        const [
          loadedSymbols,
          loadedImports,
          loadedFileRelations,
          loadedSymbolRelations,
        ] = await Promise.all([
          listSourceFileSymbols(
            currentFileId,
          ),
          listSourceFileImports(
            currentFileId,
          ),
          listSourceFileRelations(
            currentFileId,
          ),
          listSymbolRelations(
            currentFileId,
          ),
        ])

        if (cancelled) {
          return
        }

        setSymbols(loadedSymbols)
        setImports(loadedImports)
        setFileRelations(
          loadedFileRelations,
        )
        setSymbolRelations(
          loadedSymbolRelations,
        )
      } catch (caughtError) {
        if (cancelled) {
          return
        }

        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Could not load file details.",
        )
      } finally {
        if (!cancelled) {
          setDetailsLoading(false)
        }
      }
    }

    void loadFileDetails()

    return () => {
      cancelled = true
    }
  }, [selectedFileId])

  const selectedFile = useMemo(
    () =>
      files.find(
        (file) =>
          file.id === selectedFileId,
      ) ?? null,
    [files, selectedFileId],
  )

  if (loading) {
    return (
      <div className="loading-panel">
        Loading repository...
      </div>
    )
  }

  if (error && !repository) {
    return (
      <div className="error-panel">
        <p>{error}</p>
      </div>
    )
  }

  if (!repository || !snapshot) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">
          CN
        </div>

        <h3>
          Repository not ready
        </h3>

        <p>
          Analyze this repository first
          before exploring its code.
        </p>
      </div>
    )
  }

  return (
    <section className={
            selectedSymbol
            ? "repository-page repository-page-graph"
            : "repository-page"
        }>
      <div className="repository-page-heading">
        <div>
          <p className="page-kicker">
            Repository explorer
          </p>

          <h2 className="page-title">
            {repository.name}
          </h2>

          <p className="page-description">
            Explore files, symbols, imports, and
            structural relationships extracted
            from the selected snapshot.
          </p>
        </div>

        <div className="repository-snapshot-meta">
          <span className="status-badge status-ready">
            {snapshot.status}
          </span>

          <span>
            {snapshot.branch ?? "Detached"}
          </span>

          <code>
            {snapshot.commit_sha.slice(0, 7)}
          </code>
        </div>
      </div>

      <div className="repository-stats">
        <article className="overview-card">
          <span className="overview-card-label">
            Files
          </span>

          <strong>
            {files.length}
          </strong>

          <span>
            Source files discovered
          </span>
        </article>

        <article className="overview-card">
          <span className="overview-card-label">
            Selected file symbols
          </span>

          <strong>
            {symbols.length}
          </strong>

          <span>
            Classes, functions and methods
          </span>
        </article>

        <article className="overview-card">
          <span className="overview-card-label">
            Relations
          </span>

          <strong>
            {fileRelations.length +
              symbolRelations.length}
          </strong>

          <span>
            Structural relationships
          </span>
        </article>
      </div>

      <div className="repository-explorer">
        <RepositoryFileTree
            files={files}
            selectedFileId={selectedFileId}
            onSelectFile={setSelectedFileId}
        />

        {selectedSymbol ? (
            <CodeGraphPanel
                symbol={selectedSymbol}
                symbols={symbols}
                symbolRelations={symbolRelations}
                onBack={() =>
                    setSelectedSymbol(null)
                }
                onExploreSymbol={(symbol) =>
                    setSelectedSymbol(symbol)
                }
                />
            ) : (
            <FileInspector
                file={selectedFile}
                symbols={symbols}
                imports={imports}
                fileRelations={fileRelations}
                symbolRelations={symbolRelations}
                loading={detailsLoading}
                onOpenFile={setSelectedFileId}
                onSelectSymbol={setSelectedSymbol}
            />
            )}
        </div>
    </section>
  )
}

export default RepositoryPage