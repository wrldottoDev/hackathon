import { NavLink, Navigate, Outlet, Route, Routes } from "react-router-dom";
import { maskKey } from "./api";
import { useAnalysisAuth } from "./auth";
import { API_URL } from "./config";
import AlertsPage from "./pages/AlertsPage";
import FollowUpPage from "./pages/FollowUpPage";
import LoginPage from "./pages/LoginPage";
import NetworkPage from "./pages/NetworkPage";
import OverviewPage from "./pages/OverviewPage";

function ProtectedRoute() {
  const { isAuthenticated, loading } = useAnalysisAuth();

  if (loading) {
    return <div className="screen-loader">Cargando consola de análisis...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <AnalysisShell />;
}

function PublicRoute({ children }) {
  const { isAuthenticated } = useAnalysisAuth();
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  return children;
}

function AnalysisShell() {
  const { apiKey, logout } = useAnalysisAuth();

  return (
    <div className="analysis-shell">
      <aside className="analysis-sidebar">
        <div className="analysis-brand">
          <p className="analysis-kicker">Cross-Bank Monitoring</p>
          <h1>FlowLens Analytics</h1>
          <p className="analysis-copy">
            Panel externo para alertas, consolidación transaccional, red de relaciones y seguimiento profundo.
          </p>
        </div>

        <div className="analysis-bank-card">
          <p>API Analytics</p>
          <span>{API_URL}</span>
        </div>

        <nav className="analysis-nav">
          <NavLink to="/">Resumen</NavLink>
          <NavLink to="/alerts">Alertas</NavLink>
          <NavLink to="/network">Red</NavLink>
          <NavLink to="/follow-up">Follow-up</NavLink>
        </nav>

        <div className="analysis-user-card">
          <p>Sesión del panel</p>
          <span>{maskKey(apiKey)}</span>
          <button type="button" className="secondary-button" onClick={logout}>
            Salir del panel
          </button>
        </div>
      </aside>

      <main className="analysis-content">
        <Outlet />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicRoute>
            <LoginPage />
          </PublicRoute>
        }
      />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/alerts" element={<AlertsPage />} />
        <Route path="/network" element={<NetworkPage />} />
        <Route path="/follow-up" element={<FollowUpPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
