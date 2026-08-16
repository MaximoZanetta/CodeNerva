import { useEffect, useState } from "react"
import {
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom"

import {
  getAnalysisJob,
  listRepositorySnapshots,
  getProjectRepository,
  type AnalysisJob,
  type Repository,
  type Snapshot,
} from "../services/codenervaApi"

function AnalysisPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const jobId = searchParams.get("job")

  const [repository, setRepository] =
    useState<Repository | null>(null)

  const [snapshot, setSnapshot] =
    useState<Snapshot | null>(null)

  const [job, setJob] =
    useState<AnalysisJob | null>(null)

  const [loading, setLoading] = useState(true)

  const [error, setError] =
    useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      return
    }
    const currentProjectId = projectId
    let cancelled = false

    async function loadAnalysis() {
      try {
        const loadedRepository =
          await getProjectRepository(currentProjectId)

        const snapshots =
          await listRepositorySnapshots(
            loadedRepository.id,
          )

        if (cancelled) {
          return
        }

        setRepository(loadedRepository)

        if (jobId) {
          const loadedJob =
            await getAnalysisJob(jobId)

          if (cancelled) {
            return
          }

          setJob(loadedJob)

          const matchingSnapshot =
            snapshots.find(
              (item) =>
                item.id === loadedJob.snapshot_id,
            ) ?? null

          setSnapshot(matchingSnapshot)
        } else {
          setSnapshot(
            snapshots.length > 0
              ? snapshots[0]
              : null,
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
            : "Could not load analysis.",
        )
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadAnalysis()

    return () => {
      cancelled = true
    }
  }, [projectId, jobId])

  useEffect(() => {
    if (!jobId) {
      return
    }
    const currentJobId = jobId

    let cancelled = false
    let timeoutId: number | undefined

    async function pollJob() {
      try {
        const updatedJob =
          await getAnalysisJob(currentJobId)

        if (cancelled) {
          return
        }

        setJob(updatedJob)

        if (
          updatedJob.status !== "READY" &&
          updatedJob.status !== "FAILED"
        ) {
          timeoutId = window.setTimeout(
            () => {
              void pollJob()
            },
            1500,
          )
        }
      } catch (caughtError) {
        if (cancelled) {
          return
        }

        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Could not update analysis status.",
        )
      }
    }

    void pollJob()

    return () => {
      cancelled = true

      if (timeoutId !== undefined) {
        window.clearTimeout(timeoutId)
      }
    }
  }, [jobId])

  if (loading) {
    return (
      <div className="loading-panel">
        Loading analysis...
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-panel">
        <p>{error}</p>

        <button
          className="secondary-button"
          type="button"
          onClick={() =>
            navigate(
              `/projects/${projectId}`,
            )
          }
        >
          Back to overview
        </button>
      </div>
    )
  }

  if (!repository) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">
          CN
        </div>

        <h3>No repository</h3>

        <p>
          Connect a repository before running
          an analysis.
        </p>
      </div>
    )
  }

  if (!snapshot) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">
          CN
        </div>

        <h3>No analysis yet</h3>

        <p>
          Start an analysis from the project
          overview to build repository intelligence.
        </p>

        <button
          className="primary-button"
          type="button"
          onClick={() =>
            navigate(
              `/projects/${projectId}`,
            )
          }
        >
          Go to overview
        </button>
      </div>
    )
  }

  const status =
    job?.status ?? snapshot.status

  const progress =
    job?.progress ??
    (snapshot.status === "READY" ? 100 : 0)

  const ready =
    status === "READY"

  const failed =
    status === "FAILED"

  return (
    <section className="analysis-page">
      <div className="analysis-heading">
        <div>
          <p className="page-kicker">
            Repository analysis
          </p>

          <h2 className="page-title">
            {ready
              ? "Repository intelligence ready"
              : failed
                ? "Analysis failed"
                : `Analyzing ${repository.name}`}
          </h2>

          <p className="page-description">
            {ready
              ? (
                  "CodeNerva has finished building the "
                  + "structural and semantic representation "
                  + "of this repository."
                )
              : failed
                ? (
                    "CodeNerva could not complete the "
                    + "repository analysis."
                  )
                : (
                    "CodeNerva is analyzing the codebase "
                    + "and building repository intelligence."
                  )}
          </p>
        </div>

        <span
          className={`status-badge status-${status.toLowerCase()}`}
        >
          {status}
        </span>
      </div>

      <div className="analysis-progress-card">
        <div className="analysis-progress-header">
          <div>
            <span className="overview-card-label">
              Analysis progress
            </span>

            <strong>
              {ready
                ? "Analysis complete"
                : failed
                  ? "Analysis stopped"
                  : "Building intelligence"}
            </strong>
          </div>

          <span className="analysis-progress-value">
            {progress}%
          </span>
        </div>

        <div className="analysis-progress-track">
          <div
            className="analysis-progress-fill"
            style={{
              width: `${Math.min(
                Math.max(progress, 0),
                100,
              )}%`,
            }}
          />
        </div>

        <p className="analysis-progress-description">
          {ready
            ? (
                "This snapshot is ready for grounded "
                + "questions and repository exploration."
              )
            : failed
              ? (
                  job?.error_message ??
                  "The analysis encountered an error."
                )
              : (
                  "This can take a moment depending on "
                  + "the size of the repository."
                )}
        </p>
      </div>

      <div className="analysis-details-grid">
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
            Snapshot
          </span>

          <strong>
            {snapshot.branch ?? "Detached"}
          </strong>

          <span>
            {snapshot.commit_sha.slice(0, 7)}
          </span>
        </article>

        <article className="overview-card">
          <span className="overview-card-label">
            Analysis status
          </span>

          <strong>
            {status}
          </strong>

          <span>
            {progress}% complete
          </span>
        </article>
      </div>

      {ready && (
        <div className="analysis-ready-actions">
          <div>
            <p className="page-kicker">
              Intelligence ready
            </p>

            <h3>
              Explore your codebase
            </h3>

            <p>
              Ask questions grounded in the repository
              or explore its structure and relationships.
            </p>
          </div>

          <div className="analysis-action-buttons">
            <button
              className="secondary-button"
              type="button"
              onClick={() =>
                navigate(
                  `/projects/${projectId}/repository`,
                )
              }
            >
              Explore repository
            </button>

            <button
              className="primary-button"
              type="button"
              onClick={() =>
                navigate(
                  `/projects/${projectId}/chat`,
                )
              }
            >
              Ask CodeNerva
            </button>
          </div>
        </div>
      )}

      {failed && (
        <div className="analysis-failed-actions">
          <button
            className="secondary-button"
            type="button"
            onClick={() =>
              navigate(
                `/projects/${projectId}`,
              )
            }
          >
            Back to overview
          </button>
        </div>
      )}
    </section>
  )
}

export default AnalysisPage