import type { SymbolRelation } from "../../services/codenervaApi"

type SymbolRelationsPanelProps = {
  relations: SymbolRelation[]
}

function SymbolRelationsPanel({
  relations,
}: SymbolRelationsPanelProps) {
  return (
    <section className="inspector-section">
      <div className="panel-heading">
        <strong>
          Symbol relations
        </strong>

        <span className="panel-count">
          {relations.length}
        </span>
      </div>

      {relations.length > 0 ? (
        <div className="relation-list">
          {relations.map((relation) => (
            <div
              className="relation-row"
              key={relation.id}
            >
              <span className="relation-icon">
                →
              </span>

              <div>
                <strong>
                  {relation.source_symbol_name}
                  {" → "}
                  {relation.target_symbol_name}
                </strong>

                <span>
                  {relation.kind}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="section-empty">
          No symbol relations were found.
        </p>
      )}
    </section>
  )
}

export default SymbolRelationsPanel