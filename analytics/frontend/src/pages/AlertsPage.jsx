import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { analyticsRequest, formatDate } from "../api";
import { useAnalysisAuth } from "../auth";

const LEVEL_OPTIONS = ["", "low", "medium", "high"];

export default function AlertsPage() {
  const { apiKey } = useAnalysisAuth();
  const [filters, setFilters] = useState({
    bankCode: "",
    level: "",
    patternType: "",
    accountNumber: "",
  });
  const [alerts, setAlerts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadAlerts(activeFilters = filters) {
    setLoading(true);
    setError("");
    try {
      const [alertsPayload, summaryPayload] = await Promise.all([
        analyticsRequest("/alerts", {
          apiKey,
          params: {
            bank_code: activeFilters.bankCode,
            level: activeFilters.level,
            pattern_type: activeFilters.patternType,
            account_number: activeFilters.accountNumber,
            limit: 200,
          },
        }),
        analyticsRequest("/alerts/summary", { apiKey }),
      ]);
      setAlerts(alertsPayload);
      setSummary(summaryPayload);
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAlerts();
  }, [apiKey]);

  function handleSubmit(event) {
    event.preventDefault();
    loadAlerts(filters);
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Alertas</p>
          <h2>Alertas consolidadas</h2>
        </div>
        <p className="page-copy">
          Filtra por banco, nivel, patrón o cuenta y salta directo al seguimiento profundo.
        </p>
      </header>

      {error ? <p className="form-error">{error}</p> : null}

      <div className="metric-grid">
        <article className="metric-card">
          <span>Total</span>
          <strong>{summary?.total_alerts ?? 0}</strong>
        </article>
        <article className="metric-card">
          <span>Low</span>
          <strong>{summary?.low ?? 0}</strong>
        </article>
        <article className="metric-card">
          <span>Medium</span>
          <strong>{summary?.medium ?? 0}</strong>
        </article>
        <article className="metric-card accent">
          <span>High</span>
          <strong>{summary?.high ?? 0}</strong>
        </article>
      </div>

      <article className="panel">
        <div className="panel-header">
          <h3>Filtros</h3>
          <span>{loading ? "Consultando..." : `${alerts.length} resultado(s)`}</span>
        </div>
        <form className="filter-grid" onSubmit={handleSubmit}>
          <label>
            Banco
            <input
              value={filters.bankCode}
              onChange={(event) =>
                setFilters((current) => ({
                  ...current,
                  bankCode: event.target.value.toUpperCase(),
                }))
              }
              placeholder="BKA o BKB"
            />
          </label>
          <label>
            Nivel
            <select
              value={filters.level}
              onChange={(event) =>
                setFilters((current) => ({ ...current, level: event.target.value }))
              }
            >
              {LEVEL_OPTIONS.map((level) => (
                <option key={level || "all"} value={level}>
                  {level || "Todos"}
                </option>
              ))}
            </select>
          </label>
          <label>
            Patrón
            <input
              value={filters.patternType}
              onChange={(event) =>
                setFilters((current) => ({ ...current, patternType: event.target.value }))
              }
              placeholder="rapid_chain"
            />
          </label>
          <label>
            Cuenta
            <input
              value={filters.accountNumber}
              onChange={(event) =>
                setFilters((current) => ({
                  ...current,
                  accountNumber: event.target.value.toUpperCase(),
                }))
              }
              placeholder="BKA-1234567890"
            />
          </label>
          <div className="filter-actions">
            <button type="submit" className="primary-button">Aplicar filtros</button>
            <button
              type="button"
              className="secondary-button"
              onClick={() => {
                const cleared = {
                  bankCode: "",
                  level: "",
                  patternType: "",
                  accountNumber: "",
                };
                setFilters(cleared);
                loadAlerts(cleared);
              }}
            >
              Limpiar
            </button>
          </div>
        </form>
      </article>

      <article className="panel">
        <div className="panel-header">
          <h3>Listado</h3>
          <span>Hasta 200 alertas</span>
        </div>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Nivel</th>
                <th>Score</th>
                <th>Banco</th>
                <th>Cuenta</th>
                <th>Patrón</th>
                <th>Razón</th>
                <th>Fecha</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((alert) => (
                <tr key={alert.id}>
                  <td><span className={`risk-pill ${alert.level}`}>{alert.level}</span></td>
                  <td>{alert.score}</td>
                  <td>{alert.bank_code}</td>
                  <td>{alert.account_number}</td>
                  <td>{alert.pattern_type}</td>
                  <td>{alert.reason}</td>
                  <td>{formatDate(alert.created_at)}</td>
                  <td>
                    <Link
                      className="inline-link"
                      to={`/follow-up?account=${encodeURIComponent(alert.account_number)}`}
                    >
                      Ver follow-up
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!alerts.length ? <p className="empty-state">No hay alertas con los filtros actuales.</p> : null}
        </div>
      </article>
    </section>
  );
}
