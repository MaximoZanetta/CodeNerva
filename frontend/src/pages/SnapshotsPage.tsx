import { useEffect, useState } from "react"
import {
  useNavigate,
  useParams,
} from "react-router-dom"

import {
  getProjectRepository,
  listRepositorySnapshots,
  type Repository,
  type Snapshot,
} from "../services/codenervaApi"

function SnapshotsPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()

  const [repository, setRepository] =
    useState<Repository | null>(null)

  const [snapshots, setSnapshots] =
    useState<Snapshot[]>([])

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      return
    }
    const currentProjectId = projectId
    let cancelled = false

    async function loadSnapshots() {
      try {
        const loadedRepository =
          await getProjectRepository(currentProjectId)

        const loadedSnapshots =
          await listRepositorySnapshots(
            loadedRepository.id,
          )

        if (cancelled) {
          return
        }

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
            : "Could not load snapshots.",
        )
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadSnapshots()

    return () => {
      cancelled = true
    }
  }, [projectId])

  if (loading) {
    return (
      <div className="loading-panel">
        Loading snapshots...
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-panel">
        <div>
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
      </div>
    )
  }

  if (!repository) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">
          CN
        </div>

        <h3>
          Repository unavailable
        </h3>

        <p>
          Connect a repository before
          creating snapshots.
        </p>
      </div>
    )
  }

  const readySnapshots =
    snapshots.filter(
      (snapshot) =>
        snapshot.status === "READY",
    )

  return (
    <section className="snapshots-page">
      <div className="snapshots-heading">
        <div>
          <p className="page-kicker">
            Snapshots
          </p>

          <h2 className="page-title">
            Repository history
          </h2>

          <p className="page-description">
            Browse immutable repository states
            analyzed by CodeNerva.
          </p>
        </div>

        <div className="snapshots-repository-meta">
          <span>
            {repository.owner}/
            {repository.name}
          </span>

          <span className="status-badge status-ready">
            {repository.status}
          </span>
        </div>
      </div>

      <div className="snapshot-stats">
        <article className="overview-card">
          <span className="overview-card-label">
            Total snapshots
          </span>

          <strong>
            {snapshots.length}
          </strong>

          <span>
            Repository versions recorded
          </span>
        </article>

        <article className="overview-card">
          <span className="overview-card-label">
            Ready
          </span>

          <strong>
            {readySnapshots.length}
          </strong>

          <span>
            Available for intelligence
          </span>
        </article>

        <article className="overview-card">
          <span className="overview-card-label">
            Latest branch
          </span>

          <strong>
            {snapshots[0]?.branch ??
              "—"}
          </strong>

          <span>
            Most recent snapshot branch
          </span>
        </article>
      </div>

      {snapshots.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">
            CN
          </div>

          <h3>
            No snapshots yet
          </h3>

          <p>
            Run your first repository analysis
            to create an immutable snapshot.
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
            Start analysis
          </button>
        </div>
      ) : (
        <div className="snapshot-list">
          {snapshots.map(
            (snapshot, index) => {
              const ready =
                snapshot.status === "READY"

              return (
                <article
                  className="snapshot-card"
                  key={snapshot.id}
                >
                  <div className="snapshot-main">
                    <div className="snapshot-commit-icon">
                      ◇
                    </div>

                    <div className="snapshot-content">
                      <div className="snapshot-title-row">
                        <code>
                          {snapshot.commit_sha.slice(
                            0,
                            7,
                          )}
                        </code>

                        {index === 0 && (
                          <span className="snapshot-current">
                            Latest
                          </span>
                        )}

                        <span
                          className={`status-badge status-${snapshot.status.toLowerCase()}`}
                        >
                          {snapshot.status}
                        </span>
                      </div>

                      <div className="snapshot-details">
                        <span>
                          Branch
                        </span>

                        <strong>
                          {snapshot.branch ??
                            "Detached"}
                        </strong>

                        <span className="snapshot-separator">
                          ·
                        </span>

                        <span>
                          Commit
                        </span>

                        <strong className="snapshot-full-sha">
                          {snapshot.commit_sha}
                        </strong>
                      </div>

                      <p>
                        {ready
                          ? (
                              "Repository intelligence is available "
                              + "for this snapshot."
                            )
                          : (
                              "Repository intelligence is not "
                              + "ready for this snapshot yet."
                            )}
                      </p>
                    </div>
                  </div>

                  <div className="snapshot-actions">
                    <button
                      className="secondary-button"
                      type="button"
                      onClick={() =>
                        navigate(
                          `/projects/${projectId}/analysis`,
                        )
                      }
                    >
                      View analysis
                    </button>

                    <button
                      className="primary-button"
                      type="button"
                      disabled={!ready}
                      onClick={() =>
                        navigate(
                          `/projects/${projectId}/chat`,
                        )
                      }
                    >
                      Ask CodeNerva
                    </button>
                  </div>
                </article>
              )
            },
          )}
        </div>
      )}
    </section>
  )
}

export default SnapshotsPage