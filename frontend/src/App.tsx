import { Navigate, Route, Routes } from "react-router-dom"


import AppShell from "./layouts/AppShell"
import AnalysisPage from "./pages/AnalysisPage"
import ChatPage from "./pages/ChatPage"
import ProjectsPage from "./pages/ProjectsPage"
import RepositoryPage from "./pages/RepositoryPage"
import SnapshotsPage from "./pages/SnapshotsPage"
import ProjectOverviewPage from "./pages/ProjectOverviewPage"


function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route
          path="/"
          element={
            <Navigate
              to="/projects"
              replace
            />
          }
        />

        <Route
          path="/projects"
          element={<ProjectsPage />}
        />

        <Route
          path="/projects/:projectId"
          element={<ProjectOverviewPage />}
        />

        <Route
          path="/projects/:projectId/repository"
          element={<RepositoryPage />}
        />

        <Route
          path="/projects/:projectId/analysis"
          element={<AnalysisPage />}
        />

        <Route
          path="/projects/:projectId/chat"
          element={<ChatPage />}
        />

        <Route
          path="/projects/:projectId/snapshots"
          element={<SnapshotsPage />}
        />

        <Route
          path="*"
          element={
            <Navigate
              to="/projects"
              replace
            />
          }
        />
      </Route>
    </Routes>
  )
}

export default App