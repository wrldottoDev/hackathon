import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { analyticsRequest, formatDate } from "../api";
import { useAnalysisAuth } from "../auth";

const LEVEL_OPTIONS = ["", "low", "medium", "high"];
const KNOWN_PATTERNS = [
  "high_amount",
  "rapid_in_out",
  "rapid_chain",
  "burst_small_transactions",
  "star_concentration",
  "repeated_destination",
];

function parseFilters(params) {
  return {
    bankCode: (params.get("bank") || "").toUpperCase(),
    level: params.get("level") || "",
    patternType: params.get("pattern") || "",
    accountNumber: (params.get("account") || "").toUpperCase(),
  };
}

function buildSearchParams(filters) {
  const params = {};
  if (filters.bankCode) {
    params.bank = filters.bankCode;
  }
  if (filters.level) {
    params.level = filters.level;
  }
  if (filters.patternType) {
    params.pattern = filters.patternType;
  }
  if (filters.accountNumber) {
    params.account = filters.accountNumber;
  }
  return params;
}

function patternLabel(pattern) {
  return pattern.replaceAll("_", " ");
}

export default function AlertsPage() {
  const { apiKey } = useAnalysisAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState(() => parseFilters(searchParams));
  const [alerts, setAlerts] = useState([]);
  const [summary, setSummary] = useState(null);
  const [banks, setBanks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadAlerts = useCallback(
    async (activeFilters) => {
      setLoading(true);
      setError("");
      try {
        const [alertsPayload, summaryPayload, banksPayload] = await Promise.all([
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
          analyticsRequest("/banks", { apiKey }),
        ]);
        setAlerts(alertsPayload);
        setSummary(summaryPayload);
        setBanks(banksPayload);
      } catch (loadError) {
        setError(loadError.message);
      } finally {
        setLoading(false);
      }
    },
    [apiKey],
  );

  useEffect(() => {
    const nextFilters = parseFilters(searchParams);
    setFilters(nextFilters);
    loadAlerts(nextFilters);
  }, [searchParams, loadAlerts]);

  const patternOptions = useMemo(() => {
    const merged = new Set(KNOWN_PATTERNS);
    Object.keys(summary?.by_pattern || {}).forEach((pattern) => merged.add(pattern));
    return ["", ...Array.from(merged).sort()];
  }, [summary]);

  const highVisible = alerts.filter((alert) => alert.level === "high").length;
  const activeFilterTags = [
    filters.bankCode ? `Banco: ${filters.bankCode}` : null,
    filters.level ? `Nivel: ${filters.level}` : null,
    filters.patternType ? `Patrón: ${patternLabel(filters.patternType)}` : null,
    filters.accountNumber ? `Cuenta: ${filters.accountNumber}` : null,
  ].filter(Boolean);

  function commitFilters(nextFilters) {
    setSearchParams(buildSearchParams(nextFilters));
  }

  function handleSubmit(event) {
    event.preventDefault();
    commitFilters(filters);
  }

  function clearFilters() {
    commitFilters({
      bankCode: "",
      level: "",
      patternType: "",
      accountNumber: "",
    });
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Alertas</p>
          <h2>Bandeja analítica priorizada</h2>
        </div>
        <p className="page-copy">
          Filtra por banco, nivel, patrón o cuenta. Desde aquí puedes saltar al
          follow-up o abrir la red con el contexto ya aplicado.
        </p>
      </header>

      {error ? <p className="form-error">{error}</p> : null}

      <div className="metric-grid">
        <article className="metric-card">
          <span>Total consolidado</span>
          <strong>{summary?.total_alerts ?? 0}</strong>
        </article>
        <article className="metric-card">
          <span>Resultados visibles</span>
          <strong>{alerts.length}</strong>
        </article>
        <article className="metric-card">
          <span>High visibles</span>
          <strong>{highVisible}</strong>
        </article>
        <article className="metric-card accent">
          <span>Bancos activos</span>
          <strong>{banks.length}</strong>
        </article>
      </div>

      <article className="panel">
        <div className="panel-header">
          <h3>Filtros</h3>
          <span>{loading ? "Consultando..." : `${alerts.length} resultado(s)`}</span>
        </div>

        <div className="filter-chip-row">
          {LEVEL_OPTIONS.filter(Boolean).map((level) => (
            <button
              key={level}
              type="button"
              className={`filter-chip ${filters.level === level ? "active" : ""}`}
              onClick={() =>
                commitFilters({
                  ...filters,
                  level: filters.level === level ? "" : level,
                })
              }
            >
              Nivel {level}
            </button>
          ))}
          {patternOptions.filter(Boolean).slice(0, 6).map((pattern) => (
            <button
              key={pattern}
              type="button"
              className={`filter-chip ${filters.patternType === pattern ? "active" : ""}`}
              onClick={() =>
                commitFilters({
                  ...filters,
                  patternType: filters.patternType === pattern ? "" : pattern,
                })
              }
            >
              {patternLabel(pattern)}
            </button>
          ))}
        </div>

        <form className="filter-grid" onSubmit={handleSubmit}>
          <label>
            Banco
            <select
              value={filters.bankCode}
              onChange={(event) =>
                setFilters((current) => ({
                  ...current,
                  bankCode: event.target.value.toUpperCase(),
                }))
              }
            >
              <option value="">Todos</option>
              {banks.map((bank) => (
                <option key={bank.bank_code} value={bank.bank_code}>
                  {bank.bank_code} · {bank.bank_name}
                </option>
              ))}
            </select>
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
            <select
              value={filters.patternType}
              onChange={(event) =>
                setFilters((current) => ({ ...current, patternType: event.target.value }))
              }
            >
              {patternOptions.map((pattern) => (
                <option key={pattern || "all"} value={pattern}>
                  {pattern ? patternLabel(pattern) : "Todos"}
                </option>
              ))}
            </select>
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
            <button type="submit" className="primary-button">
              Aplicar filtros
            </button>
            <button type="button" className="secondary-button" onClick={clearFilters}>
              Limpiar
            </button>
          </div>
        </form>

        <div className="filter-summary">
          <div className="active-filters">
            {activeFilterTags.length ? (
              activeFilterTags.map((tag) => <span key={tag} className="active-filter-tag">{tag}</span>)
            ) : (
              <span className="active-filter-tag">Sin filtros activos</span>
            )}
          </div>
          <Link className="inline-link-button" to="/network">
            Abrir red completa
          </Link>
        </div>
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
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((alert) => (
                <tr key={alert.id} className={`alert-row ${alert.level}`}>
                  <td>
                    <span className={`risk-pill ${alert.level}`}>{alert.level}</span>
                  </td>
                  <td>{alert.score}</td>
                  <td>{alert.bank_code}</td>
                  <td>{alert.account_number}</td>
                  <td>{patternLabel(alert.pattern_type)}</td>
                  <td>{alert.reason}</td>
                  <td>{formatDate(alert.created_at)}</td>
                  <td>
                    <div className="table-actions">
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
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!alerts.length ? (
            <p className="empty-state">No hay alertas con los filtros actuales.</p>
          ) : null}
        </div>
      </article>
    </section>
  );
}
