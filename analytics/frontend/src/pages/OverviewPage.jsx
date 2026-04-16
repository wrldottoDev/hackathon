import { useEffect, useState } from "react";
import { analyticsRequest, formatDate } from "../api";
import { useAnalysisAuth } from "../auth";
import { DEMO_BANKS } from "../banks";

export default function OverviewPage() {
  const { apiKey } = useAnalysisAuth();
  const [banks, setBanks] = useState([]);
  const [summary, setSummary] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [syncResult, setSyncResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");

  async function loadDashboard() {
    setLoading(true);
    setError("");
    try {
      const [banksPayload, summaryPayload, alertsPayload] = await Promise.all([
        analyticsRequest("/banks", { apiKey }),
        analyticsRequest("/alerts/summary", { apiKey }),
        analyticsRequest("/alerts", { apiKey, params: { limit: 8 } }),
      ]);
      setBanks(banksPayload);
      setSummary(summaryPayload);
      setAlerts(alertsPayload);
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, [apiKey]);

  async function handleRegisterDemoBanks() {
    setWorking(true);
    setError("");
    try {
      for (const bank of DEMO_BANKS) {
        await analyticsRequest("/banks/register", {
          method: "POST",
          apiKey,
          body: bank,
        });
      }
      await loadDashboard();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setWorking(false);
    }
  }

  async function handleSync() {
    setWorking(true);
    setError("");
    try {
      const payload = await analyticsRequest("/transactions/fetch", { apiKey });
      setSyncResult(payload);
      await loadDashboard();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setWorking(false);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Resumen Global</p>
          <h2>Panel de consolidación</h2>
        </div>
        <p className="page-copy">
          Registra bancos, sincroniza transacciones y revisa el estado del motor analítico.
        </p>
      </header>

      {error ? <p className="form-error">{error}</p> : null}

      <div className="metric-grid">
        <article className="metric-card accent">
          <span>Bancos registrados</span>
          <strong>{banks.length}</strong>
        </article>
        <article className="metric-card">
          <span>Total alertas</span>
          <strong>{summary?.total_alerts ?? 0}</strong>
        </article>
        <article className="metric-card">
          <span>High</span>
          <strong>{summary?.high ?? 0}</strong>
        </article>
        <article className="metric-card">
          <span>Medium</span>
          <strong>{summary?.medium ?? 0}</strong>
        </article>
      </div>

      <div className="two-column-grid">
        <article className="panel">
          <div className="panel-header">
            <h3>Acciones rápidas</h3>
            <span>{working ? "Procesando..." : "Demo operativa"}</span>
          </div>
          <div className="action-stack">
            <button
              type="button"
              className="primary-button"
              onClick={handleRegisterDemoBanks}
              disabled={working}
            >
              Registrar bancos demo
            </button>
            <button
              type="button"
              className="secondary-button"
              onClick={handleSync}
              disabled={working}
            >
              Sincronizar transacciones
            </button>
          </div>
          <p className="empty-state analytics-note">
            Si ejecutaste <code>seed_flowlens.py</code> y los seeds de cada banco, esta sincronización traerá las transacciones y regenerará las alertas.
          </p>
          {syncResult ? (
            <div className="report-grid compact">
              <div className="compact-metric">
                <small>Bancos procesados</small>
                <strong>{syncResult.banks_processed}</strong>
              </div>
              <div className="compact-metric">
                <small>Transacciones vistas</small>
                <strong>{syncResult.transactions_seen}</strong>
              </div>
              <div className="compact-metric">
                <small>Alertas generadas</small>
                <strong>{syncResult.alerts_generated}</strong>
              </div>
            </div>
          ) : null}
        </article>

        <article className="panel">
          <div className="panel-header">
            <h3>Patrones detectados</h3>
            <span>{loading ? "Cargando..." : "Motor heurístico"}</span>
          </div>
          <div className="detail-list">
            {Object.entries(summary?.by_pattern || {}).map(([pattern, count]) => (
              <div className="detail-item" key={pattern}>
                <div>
                  <p>{pattern}</p>
                  <span>Patrón activo en el consolidado</span>
                </div>
                <div className="detail-item-side">
                  <strong>{count}</strong>
                </div>
              </div>
            ))}
            {!Object.keys(summary?.by_pattern || {}).length ? (
              <p className="empty-state">Aún no hay patrones detectados.</p>
            ) : null}
          </div>
        </article>
      </div>

      <div className="two-column-grid">
        <article className="panel">
          <div className="panel-header">
            <h3>Bancos observados</h3>
            <span>{banks.length} banco(s)</span>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Nombre</th>
                  <th>URL</th>
                  <th>Estado</th>
                  <th>Último fetch</th>
                </tr>
              </thead>
              <tbody>
                {banks.map((bank) => (
                  <tr key={bank.id}>
                    <td>{bank.bank_code}</td>
                    <td>{bank.bank_name}</td>
                    <td>{bank.api_url}</td>
                    <td>
                      <span
                        className={`risk-pill ${
                          bank.status === "online"
                            ? "low"
                            : bank.status === "error"
                              ? "high"
                              : "medium"
                        }`}
                      >
                        {bank.status}
                      </span>
                    </td>
                    <td>{bank.last_fetched_at ? formatDate(bank.last_fetched_at) : "Nunca"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!banks.length ? <p className="empty-state">No hay bancos registrados todavía.</p> : null}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <h3>Últimas alertas</h3>
            <span>{alerts.length} visibles</span>
          </div>
          <div className="detail-list">
            {alerts.map((alert) => (
              <div className="detail-item" key={alert.id}>
                <div>
                  <p>{alert.reason}</p>
                  <span>
                    {alert.bank_code} · {alert.account_number} · {formatDate(alert.created_at)}
                  </span>
                </div>
                <div className="detail-item-side">
                  <span className={`risk-pill ${alert.level}`}>{alert.level}</span>
                  <strong>{alert.score}</strong>
                </div>
              </div>
            ))}
            {!alerts.length ? <p className="empty-state">Sin alertas todavía.</p> : null}
          </div>
        </article>
      </div>
    </section>
  );
}
