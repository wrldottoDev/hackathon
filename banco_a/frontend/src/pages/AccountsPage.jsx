import { useEffect, useState } from "react";
import { apiRequest, formatCurrency, formatDate } from "../api";
import { useAuth } from "../auth";

export default function AccountsPage() {
  const { token } = useAuth();
  const [accounts, setAccounts] = useState([]);
  const [balance, setBalance] = useState("");
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  const fetchAccounts = () =>
    apiRequest("/accounts/my", {}, token).then(setAccounts).finally(() => setLoading(false));

  useEffect(() => { fetchAccounts(); }, [token]);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError(""); setSuccess("");
    setCreating(true);
    try {
      await apiRequest("/accounts", {
        method: "POST",
        body: JSON.stringify({ initial_balance: parseFloat(balance) || 0 }),
      }, token);
      setSuccess("Cuenta creada correctamente");
      setBalance("");
      fetchAccounts();
    } catch (err) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  };

  const totalBalance = accounts.reduce((s, a) => s + a.balance, 0);
  const largest = accounts.reduce((max, a) => (a.balance > (max?.balance ?? -1) ? a : max), null);

  return (
    <>
      <h1 className="page-title">Mis cuentas</h1>
      <p className="page-subtitle">Gestiona tus cuentas bancarias en {"{BKA}"}</p>

      <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: 20 }}>
        {/* Panel izquierdo */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="card">
            <h2 style={{ fontSize: 14, fontWeight: 700, marginBottom: 14 }}>Nueva cuenta</h2>
            {error   && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Saldo inicial (CRC)</label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  value={balance}
                  onChange={(e) => setBalance(e.target.value)}
                />
                <span className="form-hint">Deja en 0 para empezar sin saldo</span>
              </div>
              <button type="submit" className="btn btn-primary btn-full" disabled={creating}>
                {creating ? "Creando…" : "Crear cuenta"}
              </button>
            </form>
          </div>

          <div className="metric-card">
            <div className="label">Saldo total</div>
            <div className="value blue">{formatCurrency(totalBalance)}</div>
          </div>
          {largest && (
            <div className="metric-card">
              <div className="label">Cuenta con mayor saldo</div>
              <div className="value" style={{ fontSize: 16 }}>{largest.account_number}</div>
              <div style={{ color: "var(--muted)", fontSize: 13 }}>{formatCurrency(largest.balance)}</div>
            </div>
          )}
        </div>

        {/* Tabla de cuentas */}
        <div className="card">
          <h2 style={{ fontSize: 14, fontWeight: 700, marginBottom: 16 }}>
            {loading ? "Cargando…" : `${accounts.length} cuenta(s)`}
          </h2>
          {accounts.length === 0 && !loading ? (
            <div className="empty">
              <div className="empty-icon">🏦</div>
              <p>Aún no tienes cuentas. Crea una para empezar.</p>
            </div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Número de cuenta</th>
                    <th>Saldo</th>
                    <th>Moneda</th>
                    <th>Estado</th>
                    <th>Creada</th>
                  </tr>
                </thead>
                <tbody>
                  {accounts.map((a) => (
                    <tr key={a.id}>
                      <td className="mono">{a.account_number}</td>
                      <td style={{ fontWeight: 600 }}>{formatCurrency(a.balance, a.currency)}</td>
                      <td>{a.currency}</td>
                      <td>
                        <span className={`badge ${a.status === "active" ? "badge-green" : "badge-gray"}`}>
                          {a.status === "active" ? "Activa" : a.status}
                        </span>
                      </td>
                      <td>{formatDate(a.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
