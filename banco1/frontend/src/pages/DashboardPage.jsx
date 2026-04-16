import { useEffect, useState } from "react";
import { apiRequest, formatCurrency, formatDate } from "../api";
import { useAuth } from "../auth";

export default function DashboardPage() {
  const { token, user } = useAuth();
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    Promise.all([apiRequest("/accounts/my", { token }), apiRequest("/transactions/my", { token })])
      .then(([accountData, transactionData]) => {
        if (!active) {
          return;
        }
        setAccounts(accountData);
        setTransactions(transactionData);
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
  const accountIds = new Set(accounts.map((account) => account.id));
  const sentTransactions = transactions.filter((transaction) => accountIds.has(transaction.source_account_id));
  const receivedTransactions = transactions.filter((transaction) =>
    accountIds.has(transaction.destination_account_id),
  );
  const totalSent = sentTransactions.reduce((sum, transaction) => sum + transaction.amount, 0);
  const totalReceived = receivedTransactions.reduce((sum, transaction) => sum + transaction.amount, 0);

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Dashboard</p>
          <h2>Vista general de {user?.full_name}</h2>
        </div>
        <p className="page-copy">
          Revisa tus cuentas, tus saldos y la actividad reciente de tus movimientos.
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
          <span>Transferencias enviadas</span>
          <strong>{sentTransactions.length}</strong>
        </article>
        <article className="metric-card">
          <span>Transferencias recibidas</span>
          <strong>{receivedTransactions.length}</strong>
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
            <h3>Resumen de actividad</h3>
            <span>{transactions.length} movimientos</span>
          </div>
          <div className="summary-grid">
            <div>
              <small>Total enviado</small>
              <strong>{formatCurrency(totalSent)}</strong>
            </div>
            <div>
              <small>Total recibido</small>
              <strong>{formatCurrency(totalReceived)}</strong>
            </div>
            <div>
              <small>Último movimiento</small>
              <strong>{transactions[0] ? formatDate(transactions[0].created_at) : "Sin datos"}</strong>
            </div>
          </div>
          <p className="empty-state bank-note">
            El monitoreo de alertas y análisis de red se consulta desde una consola externa separada.
          </p>
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
