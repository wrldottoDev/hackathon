import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { analyticsRequest, formatCurrency, formatDate } from "../api";
import { useAnalysisAuth } from "../auth";

export default function FollowUpPage() {
  const { apiKey } = useAnalysisAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [accountInput, setAccountInput] = useState(searchParams.get("account") || "");
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadReport(accountNumber) {
    if (!accountNumber) {
      setReport(null);
      return;
    }

    setLoading(true);
    setError("");
    try {
      const payload = await analyticsRequest(
        `/accounts/${encodeURIComponent(accountNumber)}/follow-up`,
        { apiKey },
      );
      setReport(payload);
      setSearchParams({ account: accountNumber });
    } catch (loadError) {
      setReport(null);
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const initialAccount = searchParams.get("account");
    if (initialAccount) {
      setAccountInput(initialAccount);
      loadReport(initialAccount);
    }
  }, [apiKey]);

  function handleSubmit(event) {
    event.preventDefault();
    loadReport(accountInput.trim().toUpperCase());
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Follow-up</p>
          <h2>Seguimiento profundo de cuenta</h2>
        </div>
        <p className="page-copy">
          Analiza una cuenta puntual: historial, contrapartes, métricas y alertas asociadas.
        </p>
      </header>

      <article className="panel">
        <div className="panel-header">
          <h3>Buscar cuenta</h3>
          <span>{loading ? "Consultando..." : "Ej: BKA-7575078122"}</span>
        </div>
        <form className="filter-grid single-row" onSubmit={handleSubmit}>
          <label>
            Número de cuenta
            <input
              value={accountInput}
              onChange={(event) => setAccountInput(event.target.value.toUpperCase())}
              placeholder="BKA-1234567890"
            />
          </label>
          <div className="filter-actions">
            <button type="submit" className="primary-button">Consultar</button>
            <button
              type="button"
              className="secondary-button"
              onClick={() => {
                setAccountInput("");
                setReport(null);
                setSearchParams({});
              }}
            >
              Limpiar
            </button>
          </div>
        </form>
        {error ? <p className="form-error">{error}</p> : null}
      </article>

      {report ? (
        <>
          <div className="metric-grid">
            <article className="metric-card">
              <span>Cuenta</span>
              <strong>{report.account_number}</strong>
            </article>
            <article className="metric-card">
              <span>Total entrante</span>
              <strong>{formatCurrency(report.total_incoming_amount)}</strong>
            </article>
            <article className="metric-card">
              <span>Total saliente</span>
              <strong>{formatCurrency(report.total_outgoing_amount)}</strong>
            </article>
            <article className="metric-card accent">
              <span>Alertas asociadas</span>
              <strong>{report.alerts.length}</strong>
            </article>
          </div>

          <div className="two-column-grid">
            <article className="panel">
              <div className="panel-header">
                <h3>Métricas</h3>
                <span>{report.bank_code}</span>
              </div>
              <div className="report-grid">
                <div className="compact-metric">
                  <small>Incoming count</small>
                  <strong>{report.incoming_count}</strong>
                </div>
                <div className="compact-metric">
                  <small>Outgoing count</small>
                  <strong>{report.outgoing_count}</strong>
                </div>
                <div className="compact-metric">
                  <small>Montos altos</small>
                  <strong>{report.high_amount_count}</strong>
                </div>
                <div className="compact-metric">
                  <small>Promedio entrada</small>
                  <strong>{formatCurrency(report.average_incoming_amount)}</strong>
                </div>
                <div className="compact-metric">
                  <small>Promedio salida</small>
                  <strong>{formatCurrency(report.average_outgoing_amount)}</strong>
                </div>
                <div className="compact-metric">
                  <small>Contrapartes únicas</small>
                  <strong>{report.network_position.unique_counterparties}</strong>
                </div>
              </div>
            </article>

            <article className="panel">
              <div className="panel-header">
                <h3>Posición en red</h3>
                <span>Conectividad</span>
              </div>
              <div className="report-grid">
                <div className="compact-metric">
                  <small>Incoming edges</small>
                  <strong>{report.network_position.incoming_edges}</strong>
                </div>
                <div className="compact-metric">
                  <small>Outgoing edges</small>
                  <strong>{report.network_position.outgoing_edges}</strong>
                </div>
                <div className="compact-metric">
                  <small>Indirectas</small>
                  <strong>{report.network_position.indirect_counterparties}</strong>
                </div>
              </div>
              <div className="tag-list">
                {report.direct_counterparties.map((counterparty) => (
                  <span key={counterparty} className="network-chip">{counterparty}</span>
                ))}
                {!report.direct_counterparties.length ? <p className="empty-state">Sin contrapartes directas.</p> : null}
              </div>
            </article>
          </div>

          <div className="two-column-grid">
            <article className="panel">
              <div className="panel-header">
                <h3>Contrapartes frecuentes</h3>
                <span>{report.frequent_counterparties.length}</span>
              </div>
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Cuenta</th>
                      <th>Banco</th>
                      <th>Dirección</th>
                      <th>Tx</th>
                      <th>Volumen</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.frequent_counterparties.map((counterparty) => (
                      <tr key={counterparty.account_number}>
                        <td>{counterparty.account_number}</td>
                        <td>{counterparty.bank_code}</td>
                        <td>{counterparty.direction}</td>
                        <td>{counterparty.transaction_count}</td>
                        <td>{formatCurrency(counterparty.total_amount)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {!report.frequent_counterparties.length ? <p className="empty-state">Sin contrapartes frecuentes.</p> : null}
              </div>
            </article>

            <article className="panel">
              <div className="panel-header">
                <h3>Alertas asociadas</h3>
                <span>{report.alerts.length}</span>
              </div>
              <div className="detail-list">
                {report.alerts.map((alert) => (
                  <div className="detail-item" key={alert.id}>
                    <div>
                      <p>{alert.reason}</p>
                      <span>{alert.pattern_type} · {formatDate(alert.created_at)}</span>
                    </div>
                    <div className="detail-item-side">
                      <span className={`risk-pill ${alert.level}`}>{alert.level}</span>
                      <strong>{alert.score}</strong>
                    </div>
                  </div>
                ))}
                {!report.alerts.length ? <p className="empty-state">No hay alertas asociadas.</p> : null}
              </div>
            </article>
          </div>

          <article className="panel">
            <div className="panel-header">
              <h3>Transacciones recientes</h3>
              <span>{report.recent_transactions.length}</span>
            </div>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Banco</th>
                    <th>Origen</th>
                    <th>Destino</th>
                    <th>Monto</th>
                    <th>Tipo</th>
                    <th>Estado</th>
                    <th>Canal</th>
                    <th>Fecha</th>
                  </tr>
                </thead>
                <tbody>
                  {report.recent_transactions.map((transaction) => (
                    <tr key={`${transaction.bank_code}-${transaction.transaction_id}`}>
                      <td>{transaction.bank_code}</td>
                      <td>{transaction.source_account_number}</td>
                      <td>{transaction.destination_account_number}</td>
                      <td>{formatCurrency(transaction.amount)}</td>
                      <td>{transaction.transaction_type}</td>
                      <td>{transaction.status}</td>
                      <td>{transaction.channel}</td>
                      <td>{formatDate(transaction.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </article>
        </>
      ) : (
        <article className="panel">
          <p className="empty-state">Busca una cuenta para mostrar su reporte analítico.</p>
        </article>
      )}
    </section>
  );
}
