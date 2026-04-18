import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { analyticsRequest, formatDate } from "../api";
import { useAnalysisAuth } from "../auth";
import { DEMO_BANKS } from "../banks";

function patternLabel(pattern) {
  return pattern.replaceAll("_", " ");
}

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

  const onlineBanks = banks.filter((bank) => bank.status === "online").length;
  const errorBanks = banks.filter((bank) => bank.status === "error").length;
  const topPatterns = useMemo(
    () =>
      Object.entries(summary?.by_pattern || {})
        .sort((left, right) => right[1] - left[1])
        .slice(0, 6),
    [summary],
  );
  const topPattern = topPatterns[0];
  const latestFetch = useMemo(() => {
    const timestamps = banks
      .map((bank) => bank.last_fetched_at)
      .filter(Boolean)
      .sort((left, right) => new Date(right) - new Date(left));
    return timestamps[0] || syncResult?.fetched_at || null;
  }, [banks, syncResult]);

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Resumen Global</p>
          <h2>Centro de monitoreo analítico</h2>
        </div>
        <p className="page-copy">
          Registra bancos, captura transacciones y salta a la vista correcta según el
          patrón o la cuenta que necesites investigar.
        </p>
      </header>

      {error ? <p className="form-error">{error}</p> : null}

      <section className="hero-panel executive-hero">
        <div className="hero-grid">
          <div>
            <p className="eyebrow">Situación Actual</p>
            <h3>Consola ejecutiva del ecosistema FlowLens</h3>
            <p className="page-copy">
              {loading
                ? "Cargando estado consolidado..."
                : `${onlineBanks} banco(s) en línea, ${summary?.total_alerts ?? 0} alertas activas y ${
                    topPattern ? `${topPattern[1]} casos del patrón ${patternLabel(topPattern[0])}` : "sin patrones dominantes aún"
                  }.`}
            </p>
            <div className="panel-actions">
              <button
                type="button"
                className="primary-button"
                onClick={handleSync}
                disabled={working}
              >
                {working ? "Procesando..." : "Sincronizar ahora"}
              </button>
              <button
                type="button"
                className="secondary-button"
                onClick={handleRegisterDemoBanks}
                disabled={working}
              >
                Registrar bancos demo
              </button>
              <Link className="secondary-button" to="/alerts">
                Abrir alertas
              </Link>
            </div>
          </div>

          <div className="status-grid">
            <article className="status-card">
              <small>Último fetch</small>
              <strong>{latestFetch ? formatDate(latestFetch) : "Nunca"}</strong>
            </article>
            <article className="status-card">
              <small>Bancos online</small>
              <strong>{onlineBanks}</strong>
            </article>
            <article className="status-card">
              <small>Bancos con error</small>
              <strong>{errorBanks}</strong>
            </article>
            <article className="status-card">
              <small>Patrón dominante</small>
              <strong>{topPattern ? patternLabel(topPattern[0]) : "Sin datos"}</strong>
            </article>
          </div>
        </div>

        <div className="hero-stat-strip">
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
      </section>

      <div className="link-tile-grid">
        <Link className="link-tile" to="/alerts?level=high">
          <strong>Priorizar alertas high</strong>
          <span>Abre la bandeja filtrada directamente en el nivel más crítico.</span>
        </Link>
        <Link className="link-tile" to="/network">
          <strong>Explorar red transaccional</strong>
          <span>Revisa clústeres, cuentas activas y enlaces de mayor volumen.</span>
        </Link>
        <Link className="link-tile" to="/follow-up">
          <strong>Investigar una cuenta</strong>
          <span>Salta a follow-up para profundizar en métricas y contrapartes.</span>
        </Link>
      </div>

      <div className="two-column-grid">
        <article className="panel">
          <div className="panel-header">
            <h3>Patrones detectados</h3>
            <span>{loading ? "Cargando..." : "Motor heurístico"}</span>
          </div>
          <div className="detail-list">
            {topPatterns.map(([pattern, count]) => (
              <div className="detail-item" key={pattern}>
                <div>
                  <p>{patternLabel(pattern)}</p>
                  <span>Patrón activo en el consolidado analítico</span>
                  <div className="detail-item-actions">
                    <Link
                      className="inline-link-button"
                      to={`/alerts?pattern=${encodeURIComponent(pattern)}`}
                    >
                      Ver alertas
                    </Link>
                    <Link
                      className="inline-link-button"
                      to={`/alerts?pattern=${encodeURIComponent(pattern)}&level=high`}
                    >
                      Ver high
                    </Link>
                  </div>
                </div>
                <div className="detail-item-side">
                  <strong>{count}</strong>
                </div>
              </div>
            ))}
            {!topPatterns.length ? (
              <p className="empty-state">Aún no hay patrones detectados.</p>
            ) : null}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <h3>Resultado de última captura</h3>
            <span>{syncResult ? "Última ejecución" : "Aún sin captura manual"}</span>
          </div>
          <p className="empty-state analytics-note">
            Si ejecutaste <code>seed_flowlens.py</code> y los seeds locales, la
            sincronización captura transacciones de los bancos registrados y regenera alertas.
          </p>
          <div className="report-grid compact">
            <div className="compact-metric">
              <small>Bancos procesados</small>
              <strong>{syncResult?.banks_processed ?? banks.length}</strong>
            </div>
            <div className="compact-metric">
              <small>Transacciones vistas</small>
              <strong>{syncResult?.transactions_seen ?? 0}</strong>
            </div>
            <div className="compact-metric">
              <small>Alertas generadas</small>
              <strong>{syncResult?.alerts_generated ?? 0}</strong>
            </div>
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
                  <th>Estado</th>
                  <th>Último fetch</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {banks.map((bank) => (
                  <tr key={bank.id}>
                    <td>{bank.bank_code}</td>
                    <td>
                      <strong>{bank.bank_name}</strong>
                      <div style={{ color: "#8ea5a8", fontSize: "0.82rem", marginTop: 4 }}>
                        {bank.api_url}
                      </div>
                    </td>
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
                    <td>
                      <div className="table-actions">
                        <Link
                          className="inline-link-button"
                          to={`/network?bank=${encodeURIComponent(bank.bank_code)}`}
                        >
                          Ver red
                        </Link>
                        <Link
                          className="inline-link-button"
                          to={`/alerts?bank=${encodeURIComponent(bank.bank_code)}`}
                        >
                          Ver alertas
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!banks.length ? (
              <p className="empty-state">No hay bancos registrados todavía.</p>
            ) : null}
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
                  <div className="detail-item-actions">
                    <Link
                      className="inline-link-button"
                      to={`/follow-up?account=${encodeURIComponent(alert.account_number)}`}
                    >
                      Follow-up
                    </Link>
                    <Link
                      className="inline-link-button"
                      to={`/network?bank=${encodeURIComponent(alert.bank_code)}&risk=${encodeURIComponent(
                        alert.level,
                      )}&account=${encodeURIComponent(alert.account_number)}`}
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
            {!alerts.length ? <p className="empty-state">Sin alertas todavía.</p> : null}
          </div>
        </article>
      </div>
    </section>
  );
}
