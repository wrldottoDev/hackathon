import { NavLink, Navigate, Outlet, Route, Routes, useNavigate } from "react-router-dom";
import { useAuth } from "./auth";
import { BANK_NAME, BANK_TAGLINE } from "./config";
import AccountsPage from "./pages/AccountsPage";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import TransactionsPage from "./pages/TransactionsPage";
import TransferPage from "./pages/TransferPage";

function ProtectedRoute() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="screen-loader">Cargando {BANK_NAME}...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <AppShell />;
}

function PublicRoute({ children }) {
  const { isAuthenticated } = useAuth();
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  return children;
}

function AppShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="sidebar-kicker">Hackathon Demo</p>
          <h1>{BANK_NAME}</h1>
          <p className="sidebar-text">{BANK_TAGLINE}</p>
        </div>

        <nav className="nav-links">
          <NavLink to="/">Dashboard</NavLink>
          <NavLink to="/accounts">Mis cuentas</NavLink>
          <NavLink to="/transfer">Transferir</NavLink>
          <NavLink to="/transactions">Historial</NavLink>
        </nav>

        <div className="sidebar-user">
          <p>{user?.full_name}</p>
          <span>{user?.email}</span>
          <button className="ghost-button" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="content">
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
      <Route
        path="/register"
        element={
          <PublicRoute>
            <RegisterPage />
          </PublicRoute>
        }
      />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/accounts" element={<AccountsPage />} />
        <Route path="/transfer" element={<TransferPage />} />
        <Route path="/transactions" element={<TransactionsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
