import type { Symbol } from "../../services/codenervaApi"

type SymbolsPanelProps = {
  symbols: Symbol[]
  onSelectSymbol: (symbol: Symbol) => void
}

function SymbolsPanel({
  symbols,
  onSelectSymbol,
}: SymbolsPanelProps) {
  return (
    <section className="inspector-section">
      <div className="panel-heading">
        <strong>Symbols</strong>

        <span className="panel-count">
          {symbols.length}
        </span>
      </div>

      {symbols.length > 0 ? (
        <div className="symbol-list">
          {symbols.map((symbol) => (
            <button
              className="symbol-row"
              type="button"
              key={symbol.id}
              onClick={() =>
                onSelectSymbol(symbol)
              }
            >
              <div className="symbol-kind">
                {symbol.kind === "CLASS"
                  ? "C"
                  : symbol.kind === "METHOD"
                    ? "M"
                    : "ƒ"}
              </div>

              <div className="symbol-info">
                <strong>
                  {symbol.qualified_name}
                </strong>

                <span>
                  {symbol.kind}
                  {" · L"}
                  {symbol.start_line}
                  {"–"}
                  {symbol.end_line}
                </span>
              </div>

              <span>›</span>
            </button>
          ))}
        </div>
      ) : (
        <p className="section-empty">
          No symbols were extracted from this file.
        </p>
      )}
    </section>
  )
}

export default SymbolsPanel