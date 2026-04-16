import { useEffect, useState } from "react";
import { apiRequest, formatCurrency, formatDate } from "../api";
import { useAuth } from "../auth";

export default function DashboardPage() {
  const { token, user } = useAuth();
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    Promise.all([
      apiRequest("/accounts/my", { token }),
      apiRequest("/transactions/my", { token }),
      apiRequest("/risk/summary", { token }),
    ])
      .then(([accountData, transactionData, summaryData]) => {
        if (!active) {
          return;
        }
        setAccounts(accountData);
        setTransactions(transactionData);
        setSummary(summaryData);
      })
      .catch((loadError) => {
        if (active) {
          setError(loadError.message);
        }
      });

    return () => {
      active = false;
    };
  }, [token]);

  const totalBalance = accounts.reduce((sum, account) => sum + account.balance, 0);

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Dashboard</p>
          <h2>Vista general de {user?.full_name}</h2>
        </div>
        <p className="page-copy">
          Monitorea saldos, actividad reciente y señales de riesgo sobre la base cargada.
        </p>
      </header>

      {error ? <p className="form-error">{error}</p> : null}

      <div className="metric-grid">
        <article className="metric-card accent">
          <span>Balance agregado</span>
          <strong>{formatCurrency(totalBalance)}</strong>
        </article>
        <article className="metric-card">
          <span>Cuentas propias</span>
          <strong>{accounts.length}</strong>
        </article>
        <article className="metric-card">
          <span>Movimientos visibles</span>
          <strong>{transactions.length}</strong>
        </article>
        <article className="metric-card">
          <span>Alertas high</span>
          <strong>{summary?.high ?? 0}</strong>
        </article>
      </div>

      <div className="two-column-grid">
        <article className="panel">
          <div className="panel-header">
            <h3>Mis cuentas</h3>
            <span>{accounts.length ? "Activas" : "Sin cuentas"}</span>
          </div>
          <div className="card-stack">
            {accounts.length ? (
              accounts.map((account) => (
                <div className="account-card" key={account.id}>
                  <div>
                    <p>{account.account_number}</p>
                    <span>Creada el {formatDate(account.created_at)}</span>
                  </div>
                  <strong>{formatCurrency(account.balance)}</strong>
                </div>
              ))
            ) : (
              <p className="empty-state">
                Crea una cuenta desde la sección “Mis cuentas” para empezar a transferir.
              </p>
            )}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <h3>Resumen de riesgo</h3>
            <span>{summary?.total_alerts ?? 0} alertas</span>
          </div>
          {summary ? (
            <div className="summary-grid">
              <div>
                <small>Low</small>
                <strong>{summary.low}</strong>
              </div>
              <div>
                <small>Medium</small>
                <strong>{summary.medium}</strong>
              </div>
              <div>
                <small>High</small>
                <strong>{summary.high}</strong>
              </div>
            </div>
          ) : (
            <p className="empty-state">Sin datos aún.</p>
          )}
          <div className="alert-preview-list">
            {summary?.latest_alerts?.slice(0, 3).map((alert) => (
              <div className="alert-preview" key={alert.id}>
                <span className={`risk-pill ${alert.level}`}>{alert.level}</span>
                <p>{alert.reason}</p>
              </div>
            ))}
          </div>
        </article>
      </div>

      <article className="panel">
        <div className="panel-header">
          <h3>Actividad reciente</h3>
          <span>Últimos movimientos propios</span>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Origen</th>
                <th>Destino</th>
                <th>Monto</th>
                <th>Canal</th>
                <th>Fecha</th>
              </tr>
            </thead>
            <tbody>
              {transactions.slice(0, 8).map((transaction) => (
                <tr key={transaction.id}>
                  <td>#{transaction.id}</td>
                  <td>{transaction.source_account_id}</td>
                  <td>{transaction.destination_account_id}</td>
                  <td>{formatCurrency(transaction.amount)}</td>
                  <td>{transaction.channel}</td>
                  <td>{formatDate(transaction.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!transactions.length ? (
            <p className="empty-state">Todavía no hay transacciones para este usuario.</p>
          ) : null}
        </div>
      </article>
    </section>
  );
}
