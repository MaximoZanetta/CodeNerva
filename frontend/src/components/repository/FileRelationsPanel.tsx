import type { SourceFileRelation } from "../../services/codenervaApi"

type FileRelationsPanelProps = {
  relations: SourceFileRelation[]
  onOpenFile: (sourceFileId: string) => void
}

function FileRelationsPanel({
  relations,
  onOpenFile,
}: FileRelationsPanelProps) {
  return (
    <section className="inspector-section">
      <div className="panel-heading">
        <strong>File relations</strong>

        <span className="panel-count">
          {relations.length}
        </span>
      </div>

      {relations.length > 0 ? (
        <div className="relation-list">
          {relations.map((relation) => (
            <button
              className="relation-row relation-row-clickable"
              type="button"
              key={relation.id}
              onClick={() =>
                onOpenFile(
                  relation.target_source_file_id,
                )
              }
            >
              <span className="relation-icon">
                ↗
              </span>

              <div>
                <strong>
                  {relation.target_relative_path}
                </strong>

                <span>
                  {relation.kind}
                </span>
              </div>
            </button>
          ))}
        </div>
      ) : (
        <p className="section-empty">
          No file relations were found.
        </p>
      )}
    </section>
  )
}

export default FileRelationsPanel