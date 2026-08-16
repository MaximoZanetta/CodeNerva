import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"

import {
  cloneRepository,
  createSnapshot,
  getProject,
  getProjectRepository,
  listRepositorySnapshots,
  startAnalysisJob,
  type Project,
  type Repository,
  type Snapshot,
} from "../services/codenervaApi"

function ProjectOverviewPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()

  const [project, setProject] = useState<Project | null>(null)
  const [repository, setRepository] = useState<Repository | null>(null)
  const [snapshots, setSnapshots] = useState<Snapshot[]>([])

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [startingAnalysis, setStartingAnalysis] = useState(false)
  const [analysisError, setAnalysisError] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      return
    }
    const currentProjectId = projectId

    let cancelled = false

    async function loadWorkspace() {
      try {
        const loadedProject = await getProject(currentProjectId)

        let loadedRepository: Repository | null = null
        let loadedSnapshots: Snapshot[] = []

        try {
          loadedRepository = await getProjectRepository(currentProjectId)

          loadedSnapshots = await listRepositorySnapshots(
            loadedRepository.id,
          )
        } catch (caughtError) {
          if (
            caughtError instanceof Error &&
            caughtError.message.includes("not found")
          ) {
            loadedRepository = null
          } else {
            throw caughtError
          }
        }

        if (cancelled) {
          return
        }

        setProject(loadedProject)
        setRepository(loadedRepository)
        setSnapshots(loadedSnapshots)
        setError(null)
      } catch (caughtError) {
        if (cancelled) {
          return
        }

        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Unexpected error.",
        )
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadWorkspace()

    return () => {
      cancelled = true
    }
  }, [projectId])

  async function handleStartAnalysis() {
    if (!repository || !project) {
      return
    }

    setStartingAnalysis(true)
    setAnalysisError(null)

    try {
      await cloneRepository(repository.id)

      const snapshot = await createSnapshot(
        repository.id,
      )

      const job = await startAnalysisJob(
        snapshot.id,
      )

      navigate(
        `/projects/${project.id}/analysis?job=${job.id}`,
      )
    } catch (caughtError) {
      setAnalysisError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not start repository analysis.",
      )
    } finally {
      setStartingAnalysis(false)
    }
  }

  if (loading) {
    return (
      <div className="loading-panel">
        Loading project workspace...
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="error-panel">
        <div>
          <p>
            {error ?? "Project was not found."}
          </p>

          <button
            className="secondary-button"
            type="button"
            onClick={() => navigate("/projects")}
          >
            Back to projects
          </button>
        </div>
      </div>
    )
  }

  const latestSnapshot =
    snapshots.length > 0
      ? snapshots[0]
      : null

  const snapshotReady =
    latestSnapshot?.status === "READY"

  return (
    <section className="project-overview-page">
      <div className="project-hero">
        <div className="project-hero-main">
          <div className="project-avatar">
            {project.name
              .slice(0, 2)
              .toUpperCase()}
          </div>

          <div>
            <div className="project-title-row">
              <h2>
                {project.name}
              </h2>

              <span
                className={`status-badge status-${project.status.toLowerCase()}`}
              >
                {project.status}
              </span>
            </div>

            <p>
              {project.description ??
                "No project description provided."}
            </p>
          </div>
        </div>

        <button
          className="primary-button"
          type="button"
          disabled={!snapshotReady}
          onClick={() =>
            navigate(
              `/projects/${project.id}/chat`,
            )
          }
        >
          Ask CodeNerva
        </button>
      </div>

      {repository ? (
        <>
          <div className="repository-summary">
            <div>
              <p className="summary-label">
                Repository
              </p>

              <h3>
                {repository.owner}/{repository.name}
              </h3>

              <a
                href={repository.remote_url}
                target="_blank"
                rel="noreferrer"
              >
                {repository.remote_url}
              </a>
            </div>

            <span
              className={`status-badge status-${repository.status.toLowerCase()}`}
            >
              {repository.status}
            </span>
          </div>

          <div className="overview-grid">
            <article className="overview-card">
              <span className="overview-card-label">
                Repository
              </span>

              <strong>
                {repository.name}
              </strong>

              <span>
                {repository.owner}
              </span>
            </article>

            <article className="overview-card">
              <span className="overview-card-label">
                Project status
              </span>

              <strong>
                {project.status}
              </strong>

              <span>
                Ready for repository operations
              </span>
            </article>

            <article className="overview-card">
              <span className="overview-card-label">
                Intelligence
              </span>

              {latestSnapshot ? (
                <>
                  <strong>
                    {latestSnapshot.status}
                  </strong>

                  <span>
                    {latestSnapshot.branch ?? "Detached"}
                    {" · "}
                    {latestSnapshot.commit_sha.slice(0, 7)}
                  </span>
                </>
              ) : (
                <>
                  <strong>
                    Not analyzed yet
                  </strong>

                  <span>
                    Create a snapshot to begin
                  </span>
                </>
              )}
            </article>
          </div>

          <div className="overview-actions">
            <div>
              <p className="page-kicker">
                {snapshotReady
                  ? "Repository intelligence"
                  : "Next step"}
              </p>

              <h3>
                {snapshotReady
                  ? "Repository is ready"
                  : "Analyze this repository"}
              </h3>

              <p>
                {snapshotReady
                  ? (
                      "CodeNerva has finished building the structural "
                      + "and semantic representation of this snapshot."
                    )
                  : (
                      "Create a repository snapshot and let CodeNerva "
                      + "build its structural and semantic representation."
                    )}
              </p>
            </div>

            {snapshotReady ? (
              <button
                className="primary-button"
                type="button"
                onClick={() =>
                  navigate(
                    `/projects/${project.id}/chat`,
                  )
                }
              >
                Ask CodeNerva
              </button>
            ) : (
              <button
                className="primary-button"
                type="button"
                disabled={startingAnalysis}
                onClick={() =>
                  void handleStartAnalysis()
                }
              >
                {startingAnalysis
                  ? "Starting analysis..."
                  : "Start analysis"}
              </button>
            )}
          </div>

          {analysisError && (
            <div className="form-error">
              {analysisError}
            </div>
          )}
        </>
      ) : (
        <div className="empty-state">
          <div className="empty-state-icon">
            CN
          </div>

          <h3>
            Repository not connected
          </h3>

          <p>
            This project does not currently have a repository
            associated with it.
          </p>
        </div>
      )}
    </section>
  )
}

export default ProjectOverviewPage