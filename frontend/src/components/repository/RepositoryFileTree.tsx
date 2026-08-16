import { useMemo, useState } from "react"

import type { SourceFile } from "../../services/codenervaApi"

type TreeNode = {
  name: string
  path: string
  children: TreeNode[]
  file: SourceFile | null
}

type RepositoryFileTreeProps = {
  files: SourceFile[]
  selectedFileId: string | null
  onSelectFile: (fileId: string) => void
}

function buildTree(files: SourceFile[]): TreeNode[] {
  const root: TreeNode = {
    name: "",
    path: "",
    children: [],
    file: null,
  }

  for (const file of files) {
    const parts = file.relative_path.split("/")

    let current = root
    let currentPath = ""

    parts.forEach((part, index) => {
      currentPath = currentPath
        ? `${currentPath}/${part}`
        : part

      let child = current.children.find(
        (item) => item.name === part,
      )

      if (!child) {
        child = {
          name: part,
          path: currentPath,
          children: [],
          file: null,
        }

        current.children.push(child)
      }

      current = child

      if (index === parts.length - 1) {
        current.file = file
      }
    })
  }

  function sortNodes(nodes: TreeNode[]) {
    nodes.sort((a, b) => {
      const aFolder = a.file === null
      const bFolder = b.file === null

      if (aFolder !== bFolder) {
        return aFolder ? -1 : 1
      }

      return a.name.localeCompare(b.name)
    })

    for (const node of nodes) {
      sortNodes(node.children)
    }
  }

  sortNodes(root.children)

  return root.children
}

function TreeItem({
  node,
  selectedFileId,
  onSelectFile,
  depth,
}: {
  node: TreeNode
  selectedFileId: string | null
  onSelectFile: (fileId: string) => void
  depth: number
}) {
  const isFolder = node.file === null
  const [expanded, setExpanded] = useState(depth < 2)

  if (isFolder) {
    return (
      <div>
        <button
          className="tree-row tree-folder"
          type="button"
          style={{
            paddingLeft: `${12 + depth * 16}px`,
          }}
          onClick={() => setExpanded((value) => !value)}
        >
          <span className="tree-chevron">
            {expanded ? "⌄" : "›"}
          </span>

          <span className="tree-folder-icon">
            {expanded ? "▾" : "▸"}
          </span>

          <span>{node.name}</span>
        </button>

        {expanded &&
          node.children.map((child) => (
            <TreeItem
              key={child.path}
              node={child}
              selectedFileId={selectedFileId}
              onSelectFile={onSelectFile}
              depth={depth + 1}
            />
          ))}
      </div>
    )
  }

  const active =
    node.file?.id === selectedFileId

  return (
    <button
      type="button"
      className={
        active
          ? "tree-row tree-file tree-row-active"
          : "tree-row tree-file"
      }
      style={{
        paddingLeft: `${28 + depth * 16}px`,
      }}
      onClick={() => {
        if (node.file) {
          onSelectFile(node.file.id)
        }
      }}
    >
      <span className="tree-file-icon">
        ◇
      </span>

      <span>{node.name}</span>
    </button>
  )
}

function RepositoryFileTree({
  files,
  selectedFileId,
  onSelectFile,
}: RepositoryFileTreeProps) {
  const [query, setQuery] = useState("")

  const visibleFiles = useMemo(() => {
    const normalized =
      query.trim().toLowerCase()

    if (!normalized) {
      return files
    }

    return files.filter((file) =>
      file.relative_path
        .toLowerCase()
        .includes(normalized),
    )
  }, [files, query])

  const tree = useMemo(
    () => buildTree(visibleFiles),
    [visibleFiles],
  )

  return (
    <aside className="file-explorer-panel">
      <div className="panel-heading">
        <div>
          <span className="panel-eyebrow">
            Files
          </span>

          <strong>
            Repository tree
          </strong>
        </div>

        <span className="panel-count">
          {files.length}
        </span>
      </div>

      <div className="file-search">
        <input
          type="search"
          placeholder="Filter files..."
          value={query}
          onChange={(event) =>
            setQuery(event.target.value)
          }
        />
      </div>

      <div className="repository-tree">
        {tree.map((node) => (
          <TreeItem
            key={node.path}
            node={node}
            selectedFileId={selectedFileId}
            onSelectFile={onSelectFile}
            depth={0}
          />
        ))}
      </div>
    </aside>
  )
}

export default RepositoryFileTree