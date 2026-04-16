import { Navigate, NavLink, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
import { BANK_NAME } from "./config";
import AccountsPage from "./pages/AccountsPage";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import TransactionsPage from "./pages/TransactionsPage";
import TransferPage from "./pages/TransferPage";

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function PublicRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/" replace /> : children;
}

function AppShell({ children }) {
  const { user, logout } = useAuth();
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="bank-name">{BANK_NAME}</div>
          <div className="bank-tag">Portal bancario — FlowLens</div>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/" end>Inicio</NavLink>
          <NavLink to="/accounts">Cuentas</NavLink>
          <NavLink to="/transfer">Transferir</NavLink>
          <NavLink to="/transactions">Transacciones</NavLink>
        </nav>

        <div className="sidebar-user">
          <div className="user-name">{user?.full_name}</div>
          <div className="user-email">{user?.email}</div>
          <button className="logout-btn" onClick={logout}>Cerrar sesión</button>
        </div>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login"    element={<PublicRoute><LoginPage /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
      <Route path="/" element={<ProtectedRoute><AppShell><DashboardPage /></AppShell></ProtectedRoute>} />
      <Route path="/accounts" element={<ProtectedRoute><AppShell><AccountsPage /></AppShell></ProtectedRoute>} />
      <Route path="/transfer" element={<ProtectedRoute><AppShell><TransferPage /></AppShell></ProtectedRoute>} />
      <Route path="/transactions" element={<ProtectedRoute><AppShell><TransactionsPage /></AppShell></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
