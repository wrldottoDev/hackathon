import { NavLink, Navigate, Outlet, Route, Routes, useNavigate } from "react-router-dom";
import { useAnalysisAuth } from "./auth";
import AlertsPage from "./pages/AlertsPage";
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
  const { user, logout, selectedBank, banks, changeBank } = useAnalysisAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="analysis-shell">
      <aside className="analysis-sidebar">
        <div className="analysis-brand">
          <p className="analysis-kicker">External Monitoring</p>
          <h1>MultiBank Analysis Console</h1>
          <p className="analysis-copy">
            Consola separada para alertas, monitoreo transaccional y grafos entre bancos.
          </p>
        </div>

        <div className="analysis-bank-card">
          <label>
            Banco conectado
            <select
              value={selectedBank.id}
              onChange={(event) => changeBank(event.target.value)}
            >
              {banks.map((bank) => (
                <option key={bank.id} value={bank.id}>
                  {bank.label}
                </option>
              ))}
            </select>
          </label>
          <p>{selectedBank.description}</p>
          <span>{selectedBank.apiUrl}</span>
        </div>

        <nav className="analysis-nav">
          <NavLink to="/">Resumen</NavLink>
          <NavLink to="/alerts">Alertas</NavLink>
          <NavLink to="/network">Red</NavLink>
        </nav>

        <div className="analysis-user-card">
          <p>{user?.full_name}</p>
          <span>{user?.email}</span>
          <button type="button" className="secondary-button" onClick={handleLogout}>
            Cerrar sesión
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
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
