import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { analyticsRequest, formatCurrency, formatDate } from "../api";
import { useAnalysisAuth } from "../auth";

function riskRank(level) {
  return { low: 1, medium: 2, high: 3 }[level] || 0;
}

function highestRiskLevel(alerts) {
  return alerts.reduce((current, alert) => {
    return riskRank(alert.level) > riskRank(current) ? alert.level : current;
  }, "low");
}

function directionLabel(direction) {
  if (direction === "incoming") {
    return "Entrante";
  }
  if (direction === "outgoing") {
    return "Saliente";
  }
  return "Mixta";
}

export default function FollowUpPage() {
  const { apiKey } = useAnalysisAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const accountFromUrl = (searchParams.get("account") || "").trim().toUpperCase();
  const [accountInput, setAccountInput] = useState(accountFromUrl);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setAccountInput(accountFromUrl);
    if (!accountFromUrl) {
      setReport(null);
      setError("");
      return;
    }

    setLoading(true);
    setError("");
    analyticsRequest(`/accounts/${encodeURIComponent(accountFromUrl)}/follow-up`, {
      apiKey,
    })
      .then((payload) => setReport(payload))
      .catch((loadError) => {
        setReport(null);
        setError(loadError.message);
      })
      .finally(() => setLoading(false));
  }, [accountFromUrl, apiKey]);

  const maxRisk = useMemo(
    () => highestRiskLevel(report?.alerts || []),
    [report?.alerts],
  );

  function handleSubmit(event) {
    event.preventDefault();
    const normalized = accountInput.trim().toUpperCase();
    setSearchParams(normalized ? { account: normalized } : {});
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Follow-up</p>
          <h2>Seguimiento profundo de cuenta</h2>
        </div>
        <p className="page-copy">
          Abre una cuenta concreta y revisa su exposición, red de contrapartes, alertas
          asociadas y secuencia reciente de movimientos.
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
            <button type="submit" className="primary-button">
              Consultar
            </button>
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
          <section className="hero-panel followup-hero">
            <div className="followup-headline">
              <div>
                <p className="eyebrow">Cuenta Investigada</p>
                <h3 className="followup-account">{report.account_number}</h3>
                <div className="followup-meta">
                  <span className="active-filter-tag">Banco {report.bank_code}</span>
                  <span className={`risk-pill ${maxRisk}`}>Riesgo máximo {maxRisk}</span>
                  <span className="active-filter-tag">
                    {report.network_position.unique_counterparties} contrapartes únicas
                  </span>
                </div>
              </div>
              <div className="panel-actions">
                <Link
                  className="inline-link-button"
                  to={`/alerts?account=${encodeURIComponent(report.account_number)}`}
                >
                  Ver alertas
                </Link>
                <Link
                  className="inline-link-button"
                  to={`/network?bank=${encodeURIComponent(report.bank_code)}&account=${encodeURIComponent(
                    report.account_number,
                  )}`}
                >
                  Ver en red
                </Link>
              </div>
            </div>

            <div className="hero-stat-strip">
              <article className="metric-card">
                <span>Total entrante</span>
                <strong>{formatCurrency(report.total_incoming_amount)}</strong>
              </article>
              <article className="metric-card">
                <span>Total saliente</span>
                <strong>{formatCurrency(report.total_outgoing_amount)}</strong>
              </article>
              <article className="metric-card">
                <span>Alertas asociadas</span>
                <strong>{report.alerts.length}</strong>
              </article>
              <article className="metric-card accent">
                <span>Montos altos</span>
                <strong>{report.high_amount_count}</strong>
              </article>
            </div>
          </section>

          <div className="two-column-grid">
            <article className="panel">
              <div className="panel-header">
                <h3>Métricas</h3>
                <span>Comportamiento transaccional</span>
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
                  <small>Promedio entrada</small>
                  <strong>{formatCurrency(report.average_incoming_amount)}</strong>
                </div>
                <div className="compact-metric">
                  <small>Promedio salida</small>
                  <strong>{formatCurrency(report.average_outgoing_amount)}</strong>
                </div>
                <div className="compact-metric">
                  <small>Incoming edges</small>
                  <strong>{report.network_position.incoming_edges}</strong>
                </div>
                <div className="compact-metric">
                  <small>Outgoing edges</small>
                  <strong>{report.network_position.outgoing_edges}</strong>
                </div>
              </div>
            </article>

            <article className="panel">
              <div className="panel-header">
                <h3>Posición en red</h3>
                <span>Contrapartes y expansión</span>
              </div>
              <div className="context-grid">
                <div className="context-card">
                  <small>Contrapartes directas</small>
                  <div className="tag-list">
                    {report.direct_counterparties.slice(0, 10).map((counterparty) => (
                      <Link
                        key={counterparty}
                        className="network-chip"
                        to={`/follow-up?account=${encodeURIComponent(counterparty)}`}
                      >
                        {counterparty}
                      </Link>
                    ))}
                  </div>
                </div>
                <div className="context-card">
                  <small>Contrapartes indirectas</small>
                  <div className="tag-list">
                    {report.indirect_counterparties.slice(0, 10).map((counterparty) => (
                      <Link
                        key={counterparty}
                        className="network-chip"
                        to={`/follow-up?account=${encodeURIComponent(counterparty)}`}
                      >
                        {counterparty}
                      </Link>
                    ))}
                  </div>
                </div>
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
                      <th>Acción</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.frequent_counterparties.map((counterparty) => (
                      <tr key={counterparty.account_number}>
                        <td>{counterparty.account_number}</td>
                        <td>{counterparty.bank_code}</td>
                        <td>{directionLabel(counterparty.direction)}</td>
                        <td>{counterparty.transaction_count}</td>
                        <td>{formatCurrency(counterparty.total_amount)}</td>
                        <td>
                          <Link
                            className="inline-link-button"
                            to={`/follow-up?account=${encodeURIComponent(counterparty.account_number)}`}
                          >
                            Abrir
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {!report.frequent_counterparties.length ? (
                  <p className="empty-state">Sin contrapartes frecuentes.</p>
                ) : null}
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
                      <div className="detail-item-actions">
                        <Link
                          className="inline-link-button"
                          to={`/alerts?account=${encodeURIComponent(report.account_number)}&pattern=${encodeURIComponent(
                            alert.pattern_type,
                          )}`}
                        >
                          Ver patrón
                        </Link>
                        <Link
                          className="inline-link-button"
                          to={`/network?bank=${encodeURIComponent(report.bank_code)}&risk=${encodeURIComponent(
                            alert.level,
                          )}&account=${encodeURIComponent(report.account_number)}`}
                        >
                          Ver en red
                        </Link>
                      </div>
                    </div>
                    <div className="detail-item-side">
                      <span className={`risk-pill ${alert.level}`}>{alert.level}</span>
                      <strong>{alert.score}</strong>
                    </div>
                  </div>
                ))}
                {!report.alerts.length ? (
                  <p className="empty-state">No hay alertas asociadas.</p>
                ) : null}
              </div>
            </article>
          </div>

          <div className="two-column-grid">
            <article className="panel">
              <div className="panel-header">
                <h3>Timeline reciente</h3>
                <span>{report.recent_transactions.length} eventos</span>
              </div>
              <div className="timeline">
                {report.recent_transactions.map((transaction) => {
                  const isOutgoing =
                    transaction.source_account_number === report.account_number;
                  const counterparty = isOutgoing
                    ? transaction.destination_account_number
                    : transaction.source_account_number;

                  return (
                    <div
                      key={`${transaction.bank_code}-${transaction.transaction_id}`}
                      className="timeline-item"
                    >
                      <div className={`timeline-marker ${isOutgoing ? "out" : "in"}`} />
                      <div className="timeline-content">
                        <p>
                          {isOutgoing ? "Salida hacia" : "Ingreso desde"} {counterparty}
                        </p>
                        <span>
                          {transaction.transaction_type} · {transaction.channel} ·{" "}
                          {formatDate(transaction.created_at)}
                        </span>
                      </div>
                      <div className={`timeline-amount ${isOutgoing ? "out" : "in"}`}>
                        {isOutgoing ? "−" : "+"}
                        {formatCurrency(transaction.amount)}
                      </div>
                    </div>
                  );
                })}
              </div>
            </article>

            <article className="panel">
              <div className="panel-header">
                <h3>Ledger reciente</h3>
                <span>Detalle transaccional</span>
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
                    </tr>
                  </thead>
                  <tbody>
                    {report.recent_transactions.map((transaction) => (
                      <tr key={`table-${transaction.bank_code}-${transaction.transaction_id}`}>
                        <td>{transaction.bank_code}</td>
                        <td>{transaction.source_account_number}</td>
                        <td>{transaction.destination_account_number}</td>
                        <td>{formatCurrency(transaction.amount)}</td>
                        <td>{transaction.transaction_type}</td>
                        <td>{transaction.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </article>
          </div>
        </>
      ) : (
        <article className="panel">
          <p className="empty-state">Busca una cuenta para mostrar su reporte analítico.</p>
        </article>
      )}
    </section>
  );
}
