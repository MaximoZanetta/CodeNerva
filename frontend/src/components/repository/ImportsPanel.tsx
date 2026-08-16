import type { ImportReference } from "../../services/codenervaApi"

type ImportsPanelProps = {
  imports: ImportReference[]
  onOpenFile: (sourceFileId: string) => void
}

function ImportsPanel({
  imports,
  onOpenFile,
}: ImportsPanelProps) {
  return (
    <section className="inspector-section">
      <div className="panel-heading">
        <strong>Imports</strong>

        <span className="panel-count">
          {imports.length}
        </span>
      </div>

      {imports.length > 0 ? (
        <div className="relation-list">
          {imports.map((item) => {
            const resolved =
              item.resolved_source_file_id !== null

            return (
              <button
                className={
                  resolved
                    ? "relation-row relation-row-clickable"
                    : "relation-row"
                }
                type="button"
                key={item.id}
                disabled={!resolved}
                onClick={() => {
                  if (item.resolved_source_file_id) {
                    onOpenFile(
                      item.resolved_source_file_id,
                    )
                  }
                }}
              >
                <span className="relation-icon">
                  →
                </span>

                <div>
                  <strong>
                    {item.module}
                    {item.imported_name
                      ? `.${item.imported_name}`
                      : ""}
                  </strong>

                  <span>
                    {item.resolved_relative_path ??
                      "External / unresolved"}
                  </span>
                </div>
              </button>
            )
          })}
        </div>
      ) : (
        <p className="section-empty">
          No imports were found.
        </p>
      )}
    </section>
  )
}

export default ImportsPanel