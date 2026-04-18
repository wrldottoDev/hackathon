import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { apiRequest, formatCurrency, formatDate } from "../api";
import { useAuth } from "../auth";
import { BANK_NAME } from "../config";

function shortAccount(accountNumber) {
  return accountNumber ? accountNumber.slice(-6) : "------";
}

export default function DashboardPage() {
  const { token, user } = useAuth();
  const [accounts, setAccounts] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setError("");
    Promise.all([
      apiRequest("/accounts/my", {}, token),
      apiRequest("/transactions/my", {}, token),
    ])
      .then(([accs, txns]) => {
        setAccounts(accs);
        setTransactions(txns);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  const myNumbers = useMemo(
    () => new Set(accounts.map((account) => account.account_number)),
    [accounts],
  );
  const totalBalance = accounts.reduce((sum, account) => sum + account.balance, 0);
  const outgoingTransactions = transactions.filter((tx) =>
    myNumbers.has(tx.source_account_number),
  );
  const incomingTransactions = transactions.filter((tx) =>
    myNumbers.has(tx.destination_account_number),
  );
  const sent = outgoingTransactions.length;
  const received = incomingTransactions.length;
  const totalSentAmount = outgoingTransactions.reduce((sum, tx) => sum + tx.amount, 0);
  const totalReceivedAmount = incomingTransactions.reduce((sum, tx) => sum + tx.amount, 0);
  const recent = transactions.slice(0, 8);
  const interbankCount = transactions.filter(
    (tx) => tx.source_bank_code !== tx.destination_bank_code,
  ).length;
  const mainAccount = accounts.reduce(
    (largest, account) =>
      account.balance > (largest?.balance ?? -1) ? account : largest,
    null,
  );
  const greetingName = user?.full_name?.split(" ")[0] || "cliente";

  if (loading) {
    return (
      <div className="loading-state">
        <div className="spinner" />
        <span>Cargando panel bancario...</span>
      </div>
    );
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  return (
    <>
      <header className="page-header">
        <p className="page-eyebrow">{BANK_NAME}</p>
        <h1 className="page-title">Hola, {greetingName}</h1>
        <p className="page-subtitle">
          Este es tu centro operativo: saldo consolidado, cuentas activas y la
          actividad más reciente de tu portal bancario.
        </p>
      </header>

      <section className="hero-balance">
        <div className="hero-label">Saldo consolidado</div>
        <div className="hero-amount">{formatCurrency(totalBalance)}</div>
        <p className="hero-sub">
          {accounts.length
            ? `${accounts.length} cuenta(s) activa(s) monitoreadas en tiempo real.`
            : "Todavía no tienes cuentas creadas en este banco."}
        </p>
        <div className="hero-actions">
          <Link to="/transfer" className="btn btn-primary">
            Nueva transferencia
          </Link>
          <Link to="/accounts" className="btn btn-secondary">
            Administrar cuentas
          </Link>
          <Link to="/transactions" className="btn btn-secondary">
            Ver historial
          </Link>
        </div>
      </section>

      <div className="metric-grid">
        <div className="metric-card highlight">
          <div className="label">Volumen enviado</div>
          <div className="value">{formatCurrency(totalSentAmount)}</div>
        </div>
        <div className="metric-card">
          <div className="label">Volumen recibido</div>
          <div className="value accent">{formatCurrency(totalReceivedAmount)}</div>
        </div>
        <div className="metric-card">
          <div className="label">Transferencias enviadas</div>
          <div className="value">{sent}</div>
        </div>
        <div className="metric-card">
          <div className="label">Movimientos interbancarios</div>
          <div className="value">{interbankCount}</div>
        </div>
      </div>

      <div className="page-grid sidebar-layout">
        <div className="flex-col">
          <article className="panel">
            <div className="panel-header">
              <h3>Acciones rápidas</h3>
              <span>Atajos operativos</span>
            </div>
            <div className="cta-stack">
              <Link to="/transfer" className="btn btn-primary btn-full">
                Transferir fondos
              </Link>
              <Link to="/accounts" className="btn btn-secondary btn-full">
                Crear o revisar cuentas
              </Link>
              <Link to="/transactions" className="btn btn-secondary btn-full">
                Auditar movimientos
              </Link>
            </div>
          </article>

          <article className="panel">
            <div className="panel-header">
              <h3>Resumen operativo</h3>
              <span>Snapshot actual</span>
            </div>
            <div className="dashboard-stat-list">
              <div className="dashboard-stat-row">
                <span>Cuenta principal</span>
                <strong className="mono">
                  {mainAccount ? mainAccount.account_number : "Sin cuentas"}
                </strong>
              </div>
              <div className="dashboard-stat-row">
                <span>Saldo principal</span>
                <strong>
                  {mainAccount ? formatCurrency(mainAccount.balance) : formatCurrency(0)}
                </strong>
              </div>
              <div className="dashboard-stat-row">
                <span>Transferencias recibidas</span>
                <strong>{received}</strong>
              </div>
              <div className="dashboard-stat-row">
                <span>Último movimiento</span>
                <strong>
                  {recent.length ? formatDate(recent[0].created_at) : "Sin actividad"}
                </strong>
              </div>
            </div>
          </article>
        </div>

        <div className="flex-col">
          <article className="panel">
            <div className="panel-header">
              <h3>Mis cuentas</h3>
              <span>{accounts.length} activas</span>
            </div>
            {accounts.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🏦</div>
                <p>No tienes cuentas todavía. Crea una para empezar a operar.</p>
              </div>
            ) : (
              <div className="accounts-grid">
                {accounts.map((account) => (
                  <div
                    key={account.id}
                    className={`account-card ${
                      mainAccount?.account_number === account.account_number ? "selected" : ""
                    }`}
                  >
                    <div className="acc-number">{account.account_number}</div>
                    <div className="acc-balance">
                      {formatCurrency(account.balance, account.currency)}
                    </div>
                    <div className="acc-meta">
                      <span>{account.currency}</span>
                      <span>•</span>
                      <span>{account.status === "active" ? "Activa" : account.status}</span>
                      <span>•</span>
                      <span>••{shortAccount(account.account_number)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </article>

          <article className="panel">
            <div className="panel-header">
              <h3>Actividad reciente</h3>
              <span>{recent.length ? `${recent.length} movimientos` : "Sin movimientos"}</span>
            </div>
            {recent.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">💸</div>
                <p>Cuando hagas transferencias, aparecerán aquí con contexto y dirección.</p>
              </div>
            ) : (
              <div className="activity-feed">
                {recent.map((transaction) => {
                  const isOut = myNumbers.has(transaction.source_account_number);
                  const counterparty = isOut
                    ? transaction.destination_account_number
                    : transaction.source_account_number;
                  const interbank =
                    transaction.source_bank_code !== transaction.destination_bank_code;

                  return (
                    <div key={transaction.id} className="activity-item">
                      <div className={`activity-icon ${isOut ? "out" : "in"}`}>
                        {isOut ? "↗" : "↙"}
                      </div>
                      <div className="activity-body">
                        <div className="activity-desc">
                          {isOut ? "Salida hacia" : "Ingreso desde"} {counterparty}
                        </div>
                        <div className="activity-meta">
                          {interbank ? "Interbancaria" : "Interna"} · {transaction.channel} ·{" "}
                          {formatDate(transaction.created_at)}
                        </div>
                      </div>
                      <div className={`activity-amount ${isOut ? "out" : "in"}`}>
                        {isOut ? "−" : "+"}
                        {formatCurrency(transaction.amount, transaction.currency)}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </article>
        </div>
      </div>
    </>
  );
}
