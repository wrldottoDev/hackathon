import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest, formatCurrency, formatDate } from "../api";
import { useAuth } from "../auth";

export default function DashboardPage() {
  const { token, user } = useAuth();
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiRequest("/accounts/my", {}, token),
      apiRequest("/transactions/my", {}, token),
    ])
      .then(([accs, txns]) => {
        setAccounts(accs);
        setTransactions(txns);
      })
      .finally(() => setLoading(false));
  }, [token]);

  const totalBalance = accounts.reduce((s, a) => s + a.balance, 0);
  const myNumbers = new Set(accounts.map((a) => a.account_number));
  const sent = transactions.filter((t) => myNumbers.has(t.source_account_number)).length;
  const received = transactions.filter((t) => myNumbers.has(t.destination_account_number)).length;
  const recent = transactions.slice(0, 8);

  if (loading) return <div className="page-subtitle">Cargando…</div>;

  return (
    <>
      <h1 className="page-title">Bienvenido, {user?.full_name?.split(" ")[0]}</h1>
      <p className="page-subtitle">Aquí está el resumen de tu actividad bancaria</p>

      <div className="metric-grid">
        <div className="metric-card">
          <div className="label">Saldo total</div>
          <div className="value blue">{formatCurrency(totalBalance)}</div>
        </div>
        <div className="metric-card">
          <div className="label">Cuentas activas</div>
          <div className="value">{accounts.length}</div>
        </div>
        <div className="metric-card">
          <div className="label">Transferencias enviadas</div>
          <div className="value">{sent}</div>
        </div>
        <div className="metric-card">
          <div className="label">Transferencias recibidas</div>
          <div className="value">{received}</div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "20px" }}>
        {/* Cuentas */}
        <div className="card">
          <h2 style={{ fontSize: 15, fontWeight: 700, marginBottom: 14 }}>Mis cuentas</h2>
          {accounts.length === 0 ? (
            <div className="empty">
              <p>Sin cuentas aún</p>
              <Link to="/accounts" className="btn btn-primary" style={{ marginTop: 12, fontSize: 13 }}>
                Crear cuenta
              </Link>
            </div>
          ) : (
            accounts.map((a) => (
              <div key={a.id} className="account-card">
                <div className="acc-number">{a.account_number}</div>
                <div className="acc-balance">{formatCurrency(a.balance, a.currency)}</div>
                <div className="acc-currency">{a.currency} · {a.status}</div>
              </div>
            ))
          )}
        </div>

        {/* Actividad reciente */}
        <div className="card">
          <h2 style={{ fontSize: 15, fontWeight: 700, marginBottom: 14 }}>Actividad reciente</h2>
          {recent.length === 0 ? (
            <div className="empty">
              <p>Sin transacciones aún</p>
              <Link to="/transfer" className="btn btn-primary" style={{ marginTop: 12, fontSize: 13 }}>
                Hacer transferencia
              </Link>
            </div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Origen</th>
                    <th>Destino</th>
                    <th>Monto</th>
                    <th>Fecha</th>
                  </tr>
                </thead>
                <tbody>
                  {recent.map((t) => {
                    const isOut = myNumbers.has(t.source_account_number);
                    return (
                      <tr key={t.id}>
                        <td className="mono">{t.source_account_number}</td>
                        <td className="mono">{t.destination_account_number}</td>
                        <td className={isOut ? "amount-out" : "amount-in"}>
                          {isOut ? "−" : "+"}{formatCurrency(t.amount, t.currency)}
                        </td>
                        <td>{formatDate(t.created_at)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
