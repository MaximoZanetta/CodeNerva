import {
  type FormEvent,
  useEffect,
  useState,
} from "react"

import {
  useNavigate,
  useParams,
} from "react-router-dom"

import {
  askRepositoryQuestion,
  getProjectRepository,
  listRepositorySnapshots,
  type AskRepositoryResponse,
  type Repository,
  type Snapshot,
} from "../services/codenervaApi"

type ChatMessage = {
  id: string
  role: "user" | "assistant"
  content: string
  response?: AskRepositoryResponse
}

const suggestedQuestions = [
  "Explain the architecture of this repository.",
  "How does the main feature work?",
  "Where does data enter the application?",
  "What are the most important components?",
]

function ChatPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()

  const [repository, setRepository] =
    useState<Repository | null>(null)

  const [snapshot, setSnapshot] =
    useState<Snapshot | null>(null)

  const [messages, setMessages] =
    useState<ChatMessage[]>([])

  const [question, setQuestion] =
    useState("")

  const [loading, setLoading] =
    useState(true)

  const [asking, setAsking] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)

  useEffect(() => {
    if (!projectId) {
      return
    }
    const currentProjectId = projectId
    let cancelled = false

    async function loadChatContext() {
      try {
        const loadedRepository =
          await getProjectRepository(currentProjectId)

        const snapshots =
          await listRepositorySnapshots(
            loadedRepository.id,
          )

        const readySnapshot =
          snapshots.find(
            (item) =>
              item.status === "READY",
          ) ?? null

        if (!readySnapshot) {
          throw new Error(
            "This repository does not have a READY snapshot.",
          )
        }

        if (cancelled) {
          return
        }

        setRepository(loadedRepository)
        setSnapshot(readySnapshot)
        setError(null)
      } catch (caughtError) {
        if (cancelled) {
          return
        }

        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Could not load repository chat.",
        )
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadChatContext()

    return () => {
      cancelled = true
    }
  }, [projectId])

  async function submitQuestion(
    value: string,
  ) {
    const normalizedQuestion =
      value.trim()

    if (
      !normalizedQuestion ||
      !snapshot ||
      asking
    ) {
      return
    }

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: normalizedQuestion,
    }

    setMessages((current) => [
      ...current,
      userMessage,
    ])

    setQuestion("")
    setAsking(true)
    setError(null)

    try {
      const response =
        await askRepositoryQuestion(
          snapshot.id,
          normalizedQuestion,
        )

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer,
        response,
      }

      setMessages((current) => [
        ...current,
        assistantMessage,
      ])
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not answer question.",
      )
    } finally {
      setAsking(false)
    }
  }

  function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    void submitQuestion(question)
  }

  if (loading) {
    return (
      <div className="loading-panel">
        Loading CodeNerva...
      </div>
    )
  }

  if (
    error &&
    (!repository || !snapshot)
  ) {
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

  if (!repository || !snapshot) {
    return null
  }

  const empty =
    messages.length === 0

  return (
    <section className="chat-page">
      <div className="chat-page-heading">
        <div>
          <p className="page-kicker">
            Ask CodeNerva
          </p>

          <h2 className="page-title">
            Ask your codebase
          </h2>

          <p className="page-description">
            Get answers grounded in the
            repository&apos;s code, symbols,
            and structural relationships.
          </p>
        </div>

        <div className="chat-snapshot-meta">
          <span className="status-badge status-ready">
            READY
          </span>

          <span>
            {snapshot.branch ?? "Detached"}
          </span>

          <code>
            {snapshot.commit_sha.slice(
              0,
              7,
            )}
          </code>
        </div>
      </div>

      <div
        className={
          empty
            ? "chat-workspace chat-workspace-empty"
            : "chat-workspace"
        }
      >
        {empty ? (
          <div className="chat-empty-state">
            <div className="chat-empty-logo">
              CN
            </div>

            <h3>
              What do you want to understand?
            </h3>

            <p>
              Ask CodeNerva about architecture,
              execution flows, symbols,
              dependencies, or behavior.
            </p>

            <div className="suggested-questions">
              {suggestedQuestions.map(
                (suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() =>
                      void submitQuestion(
                        suggestion,
                      )
                    }
                  >
                    {suggestion}
                  </button>
                ),
              )}
            </div>
          </div>
        ) : (
          <div className="chat-messages">
            {messages.map((message) => (
              <article
                key={message.id}
                className={`chat-message chat-message-${message.role}`}
              >
                <div className="chat-message-role">
                  {message.role === "user"
                    ? "You"
                    : "CodeNerva"}
                </div>

                <div className="chat-message-content">
                  {message.content}
                </div>

                {message.response &&
                  message.response.sources.length >
                    0 && (
                    <div className="chat-sources">
                      <div className="chat-sources-heading">
                        <strong>
                          Sources
                        </strong>

                        <span>
                          {
                            message.response
                              .sources.length
                          }
                        </span>
                      </div>

                      <div className="chat-source-list">
                        {message.response.sources.map(
                          (
                            source,
                            index,
                          ) => (
                            <button
                              key={`${source.relative_path}-${source.qualified_name}-${index}`}
                              type="button"
                              className="chat-source-card"
                              onClick={() => {
                                const params = new URLSearchParams({
                                file: source.relative_path,
                                symbol: source.qualified_name,
                                })

                                navigate(
                                `/projects/${projectId}/repository?${params.toString()}`,
                                )
                            }}
                            >
                              <div className="chat-source-icon">
                                {source.symbol_kind ===
                                "CLASS"
                                  ? "C"
                                  : source.symbol_kind ===
                                      "METHOD"
                                    ? "M"
                                    : "ƒ"}
                              </div>

                              <div>
                                <strong>
                                  {
                                    source.qualified_name
                                  }
                                </strong>

                                <span>
                                  {
                                    source.relative_path
                                  }
                                </span>

                                <small>
                                  {
                                    source.symbol_kind
                                  }
                                  {" · L"}
                                  {
                                    source.start_line
                                  }
                                  {"–"}
                                  {
                                    source.end_line
                                  }
                                  {" · "}
                                  {
                                    source.retrieval_origin
                                  }
                                </small>
                              </div>

                              <span className="chat-source-arrow">
                                ›
                              </span>
                            </button>
                          ),
                        )}
                      </div>
                    </div>
                  )}
              </article>
            ))}

            {asking && (
              <article className="chat-message chat-message-assistant">
                <div className="chat-message-role">
                  CodeNerva
                </div>

                <div className="chat-thinking">
                  <span />
                  <span />
                  <span />

                  Analyzing repository context...
                </div>
              </article>
            )}
          </div>
        )}

        {error && (
          <div className="form-error">
            {error}
          </div>
        )}

        <form
          className="chat-composer"
          onSubmit={handleSubmit}
        >
          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(
                event.target.value,
              )
            }
            placeholder="Ask anything about this codebase..."
            rows={2}
            disabled={asking}
          />

          <div className="chat-composer-footer">
            <span>
              {repository.owner}/
              {repository.name}
            </span>

            <button
              className="primary-button"
              type="submit"
              disabled={
                asking ||
                !question.trim()
              }
            >
              {asking
                ? "Thinking..."
                : "Ask →"}
            </button>
          </div>
        </form>
      </div>
    </section>
  )
}

export default ChatPage