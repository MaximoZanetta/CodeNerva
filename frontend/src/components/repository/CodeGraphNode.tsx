import {
  Handle,
  Position,
  type NodeProps,
} from "@xyflow/react"

export type CodeGraphNodeData = {
  label: string
  kind: string
  isRoot: boolean
}

function CodeGraphNode({
  data,
  selected,
}: NodeProps) {
  const nodeData = data as CodeGraphNodeData

  const kindIcon =
    nodeData.kind === "CLASS"
      ? "C"
      : nodeData.kind === "METHOD"
        ? "M"
        : nodeData.kind === "FUNCTION"
          ? "ƒ"
          : "◇"

  return (
    <div
      className={[
        "codenerva-graph-node",
        nodeData.isRoot
          ? "codenerva-graph-node-root"
          : "",
        selected
          ? "codenerva-graph-node-selected"
          : "",
      ]
        .filter(Boolean)
        .join(" ")}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="graph-handle"
      />

      {nodeData.isRoot && (
        <span className="graph-root-label">
          Selected symbol
        </span>
      )}

      <div className="graph-node-content">
        <div className="graph-node-kind-icon">
          {kindIcon}
        </div>

        <div className="graph-node-text">
          <strong>{nodeData.label}</strong>
          <span>{nodeData.kind}</span>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="graph-handle"
      />
    </div>
  )
}

export default CodeGraphNode