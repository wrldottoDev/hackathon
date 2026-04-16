import { useEffect, useState } from "react";
import { apiRequest, formatCurrency, formatDate } from "../api";
import { useAuth } from "../auth";

export default function TransactionsPage() {
  const { token } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiRequest("/transactions/my", {}, token),
      apiRequest("/accounts/my", {}, token),
    ])
      .then(([txns, accs]) => {
        setTransactions(txns);
        setAccounts(accs);
      })
      .finally(() => setLoading(false));
  }, [token]);

  const myNumbers = new Set(accounts.map((a) => a.account_number));

  const totalSent = transactions
    .filter((t) => myNumbers.has(t.source_account_number))
    .reduce((s, t) => s + t.amount, 0);

  const totalReceived = transactions
    .filter((t) => myNumbers.has(t.destination_account_number))
    .reduce((s, t) => s + t.amount, 0);

  return (
    <>
      <h1 className="page-title">Historial de transacciones</h1>
      <p className="page-subtitle">Todas las transferencias relacionadas con tus cuentas</p>

      <div className="metric-grid" style={{ marginBottom: 20 }}>
        <div className="metric-card">
          <div className="label">Total transacciones</div>
          <div className="value">{transactions.length}</div>
        </div>
        <div className="metric-card">
          <div className="label">Total enviado</div>
          <div className="value" style={{ color: "var(--danger)", fontSize: 20 }}>
            {formatCurrency(totalSent)}
          </div>
        </div>
        <div className="metric-card">
          <div className="label">Total recibido</div>
          <div className="value" style={{ color: "var(--success)", fontSize: 20 }}>
            {formatCurrency(totalReceived)}
          </div>
        </div>
      </div>

      <div className="card">
        {loading ? (
          <div className="page-subtitle">Cargando transacciones…</div>
        ) : transactions.length === 0 ? (
          <div className="empty">
            <div className="empty-icon">💸</div>
            <p>No hay transacciones aún. Realiza tu primera transferencia.</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Tipo</th>
                  <th>Origen</th>
                  <th>Destino</th>
                  <th>Monto</th>
                  <th>Canal</th>
                  <th>Descripción</th>
                  <th>Fecha</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((t) => {
                  const isOut = myNumbers.has(t.source_account_number);
                  return (
                    <tr key={t.id}>
                      <td style={{ color: "var(--muted)", fontSize: 12 }}>{t.id}</td>
                      <td>
                        <span className={`badge ${isOut ? "badge-gray" : "badge-blue"}`}>
                          {isOut ? "Enviada" : "Recibida"}
                        </span>
                      </td>
                      <td className="mono">{t.source_account_number}</td>
                      <td className="mono">{t.destination_account_number}</td>
                      <td className={isOut ? "amount-out" : "amount-in"}>
                        {isOut ? "−" : "+"}{formatCurrency(t.amount, t.currency)}
                      </td>
                      <td>
                        <span className="badge badge-gray">{t.channel}</span>
                      </td>
                      <td style={{ color: "var(--muted)", maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {t.description || "—"}
                      </td>
                      <td style={{ whiteSpace: "nowrap" }}>{formatDate(t.created_at)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
