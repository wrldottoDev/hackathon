import { useEffect, useState } from "react";
import { apiRequest, formatCurrency, formatDate } from "../api";
import { useAuth } from "../auth";

export default function TransactionsPage() {
  const { token } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [accountsMap, setAccountsMap] = useState({});
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    Promise.all([
      apiRequest("/transactions/my", { token }),
      apiRequest("/accounts", { token }),
    ])
      .then(([transactionData, accountData]) => {
        if (!active) {
          return;
        }
        setTransactions(transactionData);
        setAccountsMap(
          Object.fromEntries(accountData.map((account) => [account.id, account.account_number])),
        );
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

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Historial</p>
          <h2>Transacciones del usuario</h2>
        </div>
        <p className="page-copy">
          Incluye movimientos originados por tus cuentas y transacciones recibidas.
        </p>
      </header>

      {error ? <p className="form-error">{error}</p> : null}

      <article className="panel">
        <div className="panel-header">
          <h3>Movimientos</h3>
          <span>{transactions.length} registros</span>
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
                <th>Ubicación</th>
                <th>Fecha</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((transaction) => (
                <tr key={transaction.id}>
                  <td>#{transaction.id}</td>
                  <td>{accountsMap[transaction.source_account_id] || transaction.source_account_id}</td>
                  <td>{accountsMap[transaction.destination_account_id] || transaction.destination_account_id}</td>
                  <td>{formatCurrency(transaction.amount)}</td>
                  <td>{transaction.channel}</td>
                  <td>{transaction.location}</td>
                  <td>{formatDate(transaction.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!transactions.length ? <p className="empty-state">No hay movimientos todavía.</p> : null}
        </div>
      </article>
    </section>
  );
}
