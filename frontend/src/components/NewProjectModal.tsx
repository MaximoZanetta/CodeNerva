import { type FormEvent, useState } from "react"

type NewProjectModalProps = {
  open: boolean
  onClose: () => void
  onCreated: () => void
}

type CreateProjectResponse = {
  id: string
  name: string
  description: string | null
  status: string
}

export default function NewProjectModal({
  open,
  onClose,
  onCreated,
}: NewProjectModalProps) {
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [repositoryUrl, setRepositoryUrl] = useState("")
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!open) {
    return null
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    setSubmitting(true)
    setError(null)

    try {
      const projectResponse = await fetch(
        "http://localhost:8000/api/v1/projects",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name,
            description: description.trim() || null,
          }),
        },
      )

      if (!projectResponse.ok) {
        const payload = await projectResponse.json()
        throw new Error(payload.detail ?? "Could not create project.")
      }

      const project: CreateProjectResponse =
        await projectResponse.json()

      const repositoryResponse = await fetch(
        `http://localhost:8000/api/v1/projects/${project.id}/repository`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url: repositoryUrl,
          }),
        },
      )

      if (!repositoryResponse.ok) {
        const payload = await repositoryResponse.json()
        throw new Error(
          payload.detail ?? "Could not register repository.",
        )
      }

      setName("")
      setDescription("")
      setRepositoryUrl("")

      onCreated()
      onClose()
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Unexpected error.",
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="modal-backdrop" onMouseDown={onClose}>
      <div
        className="modal-card"
        role="dialog"
        aria-modal="true"
        aria-labelledby="new-project-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="modal-header">
          <div>
            <p className="page-kicker">New project</p>
            <h2 id="new-project-title">
              Connect a codebase
            </h2>
          </div>

          <button
            className="icon-button"
            type="button"
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <form className="project-form" onSubmit={handleSubmit}>
          <label>
            <span>Project name</span>

            <input
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="ecommerce-platform"
              required
              maxLength={120}
            />
          </label>

          <label>
            <span>Description</span>

            <textarea
              value={description}
              onChange={(event) =>
                setDescription(event.target.value)
              }
              placeholder="What does this project contain?"
              maxLength={500}
              rows={3}
            />
          </label>

          <label>
            <span>GitHub repository URL</span>

            <input
              value={repositoryUrl}
              onChange={(event) =>
                setRepositoryUrl(event.target.value)
              }
              placeholder="https://github.com/owner/repository"
              type="url"
              required
            />
          </label>

          {error && (
            <div className="form-error">
              {error}
            </div>
          )}

          <div className="modal-actions">
            <button
              className="secondary-button"
              type="button"
              onClick={onClose}
              disabled={submitting}
            >
              Cancel
            </button>

            <button
              className="primary-button"
              type="submit"
              disabled={submitting}
            >
              {submitting
                ? "Creating..."
                : "Create project"}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}