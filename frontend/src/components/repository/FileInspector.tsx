import type {
  ImportReference,
  SourceFile,
  SourceFileRelation,
  Symbol,
  SymbolRelation,
} from "../../services/codenervaApi"

import FileRelationsPanel from "./FileRelationsPanel"
import ImportsPanel from "./ImportsPanel"
import SymbolRelationsPanel from "./SymbolRelationsPanel"
import SymbolsPanel from "./SymbolsPanel"

type FileInspectorProps = {
  file: SourceFile | null
  symbols: Symbol[]
  imports: ImportReference[]
  fileRelations: SourceFileRelation[]
  symbolRelations: SymbolRelation[]
  loading: boolean
  onOpenFile: (sourceFileId: string) => void
  onSelectSymbol: (symbol: Symbol) => void
}

function formatBytes(bytes: number) {
  if (bytes < 1024) {
    return `${bytes} B`
  }

  const kb = bytes / 1024

  if (kb < 1024) {
    return `${kb.toFixed(1)} KB`
  }

  return `${(kb / 1024).toFixed(1)} MB`
}

function FileInspector({
  file,
  symbols,
  imports,
  fileRelations,
  symbolRelations,
  loading,
  onOpenFile,
  onSelectSymbol,
}: FileInspectorProps) {
  if (!file) {
    return (
      <div className="file-inspector">
        <div className="empty-state">
          <h3>Select a file</h3>

          <p>
            Choose a source file to inspect its code intelligence.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="file-inspector">
      <div className="file-inspector-header">
        <p className="panel-eyebrow">
          Selected file
        </p>

        <h3>
          {file.relative_path}
        </h3>

        <div className="file-meta-row">
          <span>{file.language}</span>

          <span>
            {formatBytes(file.size_bytes)}
          </span>

          <code>
            {file.content_hash.slice(0, 10)}
          </code>
        </div>
      </div>

      {loading ? (
        <div className="inspector-loading">
          Loading code intelligence...
        </div>
      ) : (
        <div className="inspector-sections">
          <SymbolsPanel
            symbols={symbols}
            onSelectSymbol={onSelectSymbol}
          />

          <ImportsPanel
            imports={imports}
            onOpenFile={onOpenFile}
          />

          <FileRelationsPanel
            relations={fileRelations}
            onOpenFile={onOpenFile}
          />

          <SymbolRelationsPanel
            relations={symbolRelations}
          />
        </div>
      )}
    </div>
  )
}

export default FileInspector