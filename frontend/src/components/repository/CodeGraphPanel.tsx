import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react"

import {
  Background,
  BackgroundVariant,
  Controls,
  ReactFlow,
  type Edge,
  type Node,
  type NodeMouseHandler,
} from "@xyflow/react"

import "@xyflow/react/dist/style.css"

import {
  getSymbolCalls,
  type Symbol,
  type SymbolRelation,
} from "../../services/codenervaApi"

import CodeGraphNode, {
  type CodeGraphNodeData,
} from "./CodeGraphNode"

type CodeGraphPanelProps = {
  symbol: Symbol
  symbols: Symbol[]
  symbolRelations: SymbolRelation[]
  onBack: () => void
  onExploreSymbol: (symbol: Symbol) => void
}

type GraphNode = Node<CodeGraphNodeData>

const nodeTypes = {
  codeSymbol: CodeGraphNode,
}

function CodeGraphPanel({
  symbol,
  symbols,
  symbolRelations,
  onBack,
  onExploreSymbol,
}: CodeGraphPanelProps) {
  const [loading, setLoading] = useState(true)
  const [error, setError] =
    useState<string | null>(null)

  const [nodes, setNodes] =
    useState<GraphNode[]>([])

  const [edges, setEdges] =
    useState<Edge[]>([])

  const [selectedNodeId, setSelectedNodeId] =
    useState<string>(symbol.id)

  const symbolById = useMemo(
    () =>
      new Map(
        symbols.map((item) => [
          item.id,
          item,
        ]),
      ),
    [symbols],
  )

  useEffect(() => {
    let cancelled = false

    async function loadGraph() {
      setLoading(true)

      try {
        const traversal =
          await getSymbolCalls(
            symbol.id,
            2,
          )

        if (cancelled) {
          return
        }

        const graphNodes: GraphNode[] = []

        const traversalNodeIds =
          new Set<string>()

        traversalNodeIds.add(
          traversal.root_symbol_id,
        )

        graphNodes.push({
          id: traversal.root_symbol_id,
          type: "codeSymbol",
          position: {
            x: 380,
            y: 40,
          },
          data: {
            label:
              traversal.root_symbol_name,
            kind: symbol.kind,
            isRoot: true,
          },
        })

        const nodesByDepth =
          new Map<number, number>()

        for (const node of traversal.nodes) {
          traversalNodeIds.add(
            node.symbol_id,
          )

          const index =
            nodesByDepth.get(
              node.depth,
            ) ?? 0

          nodesByDepth.set(
            node.depth,
            index + 1,
          )

          const knownSymbol =
            symbolById.get(
              node.symbol_id,
            )

          graphNodes.push({
            id: node.symbol_id,
            type: "codeSymbol",
            position: {
              x: 100 + index * 260,
              y: 80 + node.depth * 190,
            },
            data: {
              label: node.symbol_name,
              kind:
                knownSymbol?.kind ??
                "SYMBOL",
              isRoot: false,
            },
          })
        }

        const graphEdges: Edge[] =
          symbolRelations
            .filter(
              (relation) =>
                relation.kind === "CALLS" &&
                traversalNodeIds.has(
                  relation.source_symbol_id,
                ) &&
                traversalNodeIds.has(
                  relation.target_symbol_id,
                ),
            )
            .map((relation) => ({
              id: relation.id,
              source:
                relation.source_symbol_id,
              target:
                relation.target_symbol_id,
              type: "smoothstep",
              label: "CALLS",
              animated: false,
              style: {
                stroke: "#64748b",
                strokeWidth: 1.4,
              },
              labelStyle: {
                fill: "#94a3b8",
                fontSize: 9,
                fontWeight: 600,
              },
              labelBgStyle: {
                fill: "#0b1422",
                fillOpacity: 0.94,
              },
              labelBgPadding: [
                5,
                3,
              ],
              labelBgBorderRadius: 5,
              markerEnd: {
                type: "arrowclosed",
                color: "#64748b",
              },
            }))

        setNodes(graphNodes)
        setEdges(graphEdges)
        setSelectedNodeId(
          traversal.root_symbol_id,
        )
        setError(null)
      } catch (caughtError) {
        if (cancelled) {
          return
        }

        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Could not load code graph.",
        )
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadGraph()

    return () => {
      cancelled = true
    }
  }, [
    symbol.id,
    symbol.kind,
    symbolById,
    symbolRelations,
  ])

  const selectedNode = useMemo(
    () =>
      nodes.find(
        (node) =>
          node.id === selectedNodeId,
      ) ?? null,
    [nodes, selectedNodeId],
  )

  const selectedSymbol = useMemo(
    () =>
      selectedNode
        ? symbolById.get(
            selectedNode.id,
          ) ?? null
        : null,
    [selectedNode, symbolById],
  )

  const incomingRelations = useMemo(
    () =>
      selectedNode
        ? symbolRelations.filter(
            (relation) =>
              relation.target_symbol_id ===
              selectedNode.id,
          )
        : [],
    [selectedNode, symbolRelations],
  )

  const outgoingRelations = useMemo(
    () =>
      selectedNode
        ? symbolRelations.filter(
            (relation) =>
              relation.source_symbol_id ===
              selectedNode.id,
          )
        : [],
    [selectedNode, symbolRelations],
  )

  const handleNodeClick =
    useCallback<NodeMouseHandler>(
      (_, node) => {
        setSelectedNodeId(node.id)
      },
      [],
    )

  return (
    <div className="code-graph-panel">
      <div className="code-graph-header">
        <div>
          <p className="panel-eyebrow">
            Code graph
          </p>

          <h3>
            {symbol.qualified_name}
          </h3>

          <p>
            Explore call relationships
            around the selected symbol.
          </p>
        </div>

        <button
          className="secondary-button"
          type="button"
          onClick={onBack}
        >
          Back to explorer
        </button>
      </div>

      {loading ? (
        <div className="inspector-loading">
          Building code graph...
        </div>
      ) : error ? (
        <div className="error-panel">
          <p>{error}</p>
        </div>
      ) : (
        <>
          <div className="code-graph-canvas">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              nodeTypes={nodeTypes}
              onNodeClick={
                handleNodeClick
              }
              fitView
              fitViewOptions={{
                padding: 0.25,
              }}
              minZoom={0.3}
              maxZoom={1.8}
            >
              <Background
                variant={
                  BackgroundVariant.Dots
                }
                gap={20}
                size={1}
              />

              <Controls
                showInteractive={false}
              />
            </ReactFlow>
          </div>

          {selectedNode && (
            <div className="graph-inspector">
              <div className="graph-inspector-main">
                <div className="graph-inspector-icon">
                  {selectedNode.data.kind ===
                  "CLASS"
                    ? "C"
                    : selectedNode.data
                          .kind ===
                        "METHOD"
                      ? "M"
                      : "ƒ"}
                </div>

                <div>
                  <p className="panel-eyebrow">
                    Selected node
                  </p>

                  <h4>
                    {
                      selectedNode.data
                        .label
                    }
                  </h4>

                  <div className="graph-node-meta">
                    <span>
                      {
                        selectedNode.data
                          .kind
                      }
                    </span>

                    {selectedSymbol && (
                      <>
                        <span>
                          L
                          {
                            selectedSymbol.start_line
                          }
                          –
                          {
                            selectedSymbol.end_line
                          }
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <div className="graph-relation-summary">
                <div>
                  <span>Calls</span>
                  <strong>
                    {
                      outgoingRelations.length
                    }
                  </strong>
                </div>

                <div>
                  <span>Called by</span>
                  <strong>
                    {
                      incomingRelations.length
                    }
                  </strong>
                </div>
              </div>

              <button
                className="primary-button"
                type="button"
                disabled={
                  !selectedSymbol ||
                  selectedSymbol.id ===
                    symbol.id
                }
                onClick={() => {
                  if (selectedSymbol) {
                    onExploreSymbol(
                      selectedSymbol,
                    )
                  }
                }}
              >
                {selectedNode.id ===
                symbol.id
                  ? "Current root"
                  : selectedSymbol
                    ? "Explore symbol"
                    : "Symbol metadata unavailable"}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default CodeGraphPanel