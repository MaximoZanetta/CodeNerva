import { NavLink, Outlet, useParams } from "react-router-dom"

function AppShell() {
  const { projectId } = useParams()

  const projectNavItems = projectId
    ? [
        {
          label: "Overview",
          to: `/projects/${projectId}`,
          end: true,
        },
        {
          label: "Repository",
          to: `/projects/${projectId}/repository`,
        },
        {
          label: "Analysis",
          to: `/projects/${projectId}/analysis`,
        },
        {
          label: "Ask CodeNerva",
          to: `/projects/${projectId}/chat`,
        },
        {
          label: "Snapshots",
          to: `/projects/${projectId}/snapshots`,
        },
      ]
    : []

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            CN
          </div>

          <div>
            <div className="brand-name">
              CodeNerva
            </div>

            <div className="brand-subtitle">
              Code Intelligence
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <NavLink
            to="/projects"
            end={!projectId}
            className={({ isActive }) =>
              isActive
                ? "nav-link nav-link-active"
                : "nav-link"
            }
          >
            Projects
          </NavLink>

          {projectId && (
            <>
              <div className="sidebar-section-label">
                Workspace
              </div>

              {projectNavItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) =>
                    isActive
                      ? "nav-link nav-link-active"
                      : "nav-link"
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </>
          )}
        </nav>

        <div className="sidebar-footer">
          <span className="status-dot" />
          Backend connected
        </div>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <div>
            <p className="topbar-eyebrow">
              {projectId ? "Project workspace" : "Workspace"}
            </p>

            <h1 className="topbar-title">
              {projectId
                ? "Repository Intelligence"
                : "CodeNerva"}
            </h1>
          </div>
        </header>

        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default AppShell