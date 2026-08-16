import { useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom"
import NewProjectModal from "../components/NewProjectModal"

type Project = {
  id: string
  name: string
  description: string | null
  status: string
}

type ListProjectsResponse = {
  projects: Project[]
}

const PROJECTS_URL = "http://localhost:8000/api/v1/projects"

async function fetchProjects(): Promise<Project[]> {
  const response = await fetch(PROJECTS_URL)

  if (!response.ok) {
    throw new Error("Could not load projects.")
  }

  const payload: ListProjectsResponse = await response.json()

  return payload.projects
}

function ProjectsPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [query, setQuery] = useState("")
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function loadProjects() {
    setLoading(true)
    setError(null)

    try {
      const loadedProjects = await fetchProjects()

      setProjects(loadedProjects)
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Unexpected error.",
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let cancelled = false

    void fetchProjects()
      .then((loadedProjects) => {
        if (cancelled) {
          return
        }

        setProjects(loadedProjects)
        setError(null)
      })
      .catch((caughtError: unknown) => {
        if (cancelled) {
          return
        }

        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Unexpected error.",
        )
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  const visibleProjects = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase()

    if (!normalizedQuery) {
      return projects
    }

    return projects.filter((project) =>
      project.name.toLowerCase().includes(normalizedQuery),
    )
  }, [projects, query])

  return (
    <section className="projects-page">
      <div className="page-heading-row">
        <div>
          <p className="page-kicker">Projects</p>

          <h2 className="page-title">
            Your codebases
          </h2>

          <p className="page-description">
            Connect repositories, analyze their structure, and ask CodeNerva
            questions grounded in the code.
          </p>
        </div>

        <button
          className="primary-button"
          type="button"
          onClick={() => setModalOpen(true)}
        >
          + New Project
        </button>
      </div>

      <div className="projects-toolbar">
        <div className="search-field">
          <span className="search-icon">
            ⌕
          </span>

          <input
            type="search"
            placeholder="Search projects..."
            value={query}
            onChange={(event) =>
              setQuery(event.target.value)
            }
          />
        </div>
      </div>

      {loading ? (
        <div className="loading-panel">
          Loading projects...
        </div>
      ) : error ? (
        <div className="error-panel">
          <div>
            <p>{error}</p>

            <button
              className="secondary-button"
              type="button"
              onClick={() => void loadProjects()}
            >
              Try again
            </button>
          </div>
        </div>
      ) : visibleProjects.length > 0 ? (
        <div className="project-grid">
          {visibleProjects.map((project) => (
            <article
              className="project-card"
              key={project.id}
            >
              <div className="project-card-header">
                <div className="project-icon">
                  {project.name
                    .slice(0, 2)
                    .toUpperCase()}
                </div>

                <span
                  className={`status-badge status-${project.status.toLowerCase()}`}
                >
                  {project.status}
                </span>
              </div>

              <div className="project-card-body">
                <h3>
                  {project.name}
                </h3>

                <p>
                  {project.description ??
                    "No description provided."}
                </p>
              </div>

              <div className="project-card-footer">
                <button
                className="secondary-button"
                type="button"
                onClick={() =>
                    navigate(`/projects/${project.id}`)
                }
                >
                Open workspace
                </button>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <div className="empty-state-icon">
            CN
          </div>

          <h3>
            {query
              ? "No projects found"
              : "No projects yet"}
          </h3>

          <p>
            {query
              ? "No project matches your current search."
              : (
                  "Create your first CodeNerva project and connect a GitHub "
                  + "repository to begin analyzing its codebase."
                )}
          </p>

          {!query && (
            <button
              className="primary-button"
              type="button"
              onClick={() => setModalOpen(true)}
            >
              + New Project
            </button>
          )}
        </div>
      )}

      <NewProjectModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onCreated={() => void loadProjects()}
      />
    </section>
  )
}

export default ProjectsPage