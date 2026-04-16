import { useEffect, useState } from "react";
import { Background, Controls, MiniMap, ReactFlow } from "@xyflow/react";
import { bankRequest, formatCurrency, formatDate } from "../api";
import { useAnalysisAuth } from "../auth";

const RISK_OPTIONS = ["all", "low", "medium", "high"];

function riskColor(risk) {
  if (risk === "high") {
    return "#ff6b6b";
  }
  if (risk === "medium") {
    return "#f4b740";
  }
  return "#29c3a5";
}

function riskLabel(risk) {
  if (risk === "all") {
    return "Todas";
  }
  return risk.toUpperCase();
}

function buildQuery(params) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  return query ? `?${query}` : "";
}

function buildFlow(graph) {
  const focusNodes = graph.nodes.filter((node) => node.is_focus);
  const contextNodes = graph.nodes.filter((node) => !node.is_focus);
  const centerX = 620;
  const centerY = 350;
  const nodes = [];

  if (focusNodes.length) {
    focusNodes.forEach((node, index) => {
      nodes.push({
        id: node.id,
        position: {
          x: 260,
          y: centerY - 100 + index * 145,
        },
        data: {
          label: `${node.owner_name} · ${node.account_number} · ${formatCurrency(node.balance)}`,
        },
        style: {
          background: "#102c31",
          border: `3px solid ${riskColor(node.risk)}`,
          borderRadius: "22px",
          color: "#f7fbfc",
          width: 270,
          padding: "16px",
          fontSize: "12px",
          fontWeight: 600,
        },
      });
    });

    const radius = Math.max(220, contextNodes.length * 18);
    contextNodes.forEach((node, index) => {
      const angle = (Math.PI * 2 * index) / Math.max(contextNodes.length, 1);
      nodes.push({
        id: node.id,
        position: {
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle),
        },
        data: {
          label: `${node.owner_name} · ${node.account_number.slice(-4)} · ${formatCurrency(node.balance)}`,
        },
        style: {
          background: "#102126",
          border: `2px solid ${riskColor(node.risk)}`,
          borderRadius: "18px",
          color: "#f7fbfc",
          width: 220,
          padding: "14px",
          fontSize: "12px",
        },
      });
    });
  } else {
    const total = Math.max(graph.nodes.length, 1);
    const radius = Math.max(260, total * 14);
    graph.nodes.forEach((node, index) => {
      const angle = (Math.PI * 2 * index) / total;
      nodes.push({
        id: node.id,
        position: {
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle),
        },
        data: {
          label: `${node.owner_name} · ${node.account_number.slice(-4)} · ${formatCurrency(node.balance)}`,
        },
        style: {
          background: "#102126",
          border: `2px solid ${riskColor(node.risk)}`,
          borderRadius: "18px",
          color: "#f7fbfc",
          width: 220,
          padding: "14px",
          fontSize: "12px",
        },
      });
    });
  }

  const edges = graph.edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: formatCurrency(edge.amount),
    animated: edge.risk !== "low",
    style: {
      stroke: riskColor(edge.risk),
      strokeWidth: edge.risk === "high" ? 3.4 : edge.risk === "medium" ? 2.6 : 1.8,
    },
    labelStyle: {
      fill: "#8ea5a8",
      fontSize: 11,
      fontWeight: 600,
    },
  }));

  return { nodes, edges };
}

function downloadReport(report, bankLabel) {
  const lines = [
    `${bankLabel} - Reporte de Red Transaccional`,
    `Generado: ${formatDate(report.generated_at)}`,
    `Cliente: ${report.user.full_name} <${report.user.email}>`,
    `Filtro de riesgo: ${riskLabel(report.risk_filter)}`,
    `Cuentas: ${report.accounts.map((account) => account.account_number).join(", ") || "Sin cuentas"}`,
    `Total transacciones: ${report.total_transactions}`,
    `Total enviado: ${formatCurrency(report.total_sent)}`,
    `Total recibido: ${formatCurrency(report.total_received)}`,
    `Contrapartes distintas: ${report.distinct_counterparties}`,
    `Transacciones con alerta: ${report.flagged_transactions}`,
    `Distribucion riesgo: low=${report.low}, medium=${report.medium}, high=${report.high}`,
    "",
    "Top contrapartes:",
    ...report.top_counterparties.map(
      (counterparty) =>
        `- ${counterparty.full_name} (${counterparty.email}) | tx=${counterparty.transaction_count} | volumen=${formatCurrency(counterparty.total_amount)}`,
    ),
    "",
    "Transacciones recientes:",
    ...report.recent_transactions.map(
      (transaction) =>
        `- #${transaction.transaction_id} | ${formatDate(transaction.created_at)} | ${transaction.source_label} -> ${transaction.destination_label} | ${formatCurrency(transaction.amount)} | ${transaction.risk} | ${transaction.channel} | ${transaction.location}`,
    ),
  ];

  const blob = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `analysis-report-${report.user.id}-${report.risk_filter}.txt`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(url);
}

export default function NetworkPage() {
  const { token, selectedBank } = useAnalysisAuth();
  const [users, setUsers] = useState([]);
  const [riskFilter, setRiskFilter] = useState("all");
  const [selectedUserId, setSelectedUserId] = useState("");
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const [report, setReport] = useState(null);
  const [graphLoading, setGraphLoading] = useState(true);
  const [reportLoading, setReportLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    bankRequest(selectedBank.apiUrl, "/users", { token })
      .then((payload) => setUsers(payload))
      .catch((loadError) => setError(loadError.message));
  }, [selectedBank.apiUrl, token]);

  useEffect(() => {
    const query = buildQuery({
      risk: riskFilter,
      user_id: selectedUserId,
    });

    setGraphLoading(true);
    setError("");

    bankRequest(selectedBank.apiUrl, `/network/graph${query}`, { token })
      .then((payload) => setGraph(buildFlow(payload)))
      .catch((loadError) => setError(loadError.message))
      .finally(() => setGraphLoading(false));
  }, [riskFilter, selectedBank.apiUrl, selectedUserId, token]);

  useEffect(() => {
    if (!selectedUserId) {
      setReport(null);
      return;
    }

    const query = buildQuery({
      risk: riskFilter,
      user_id: selectedUserId,
    });

    setReportLoading(true);
    bankRequest(selectedBank.apiUrl, `/network/report${query}`, { token })
      .then((payload) => setReport(payload))
      .catch((loadError) => setError(loadError.message))
      .finally(() => setReportLoading(false));
  }, [riskFilter, selectedBank.apiUrl, selectedUserId, token]);

  const selectedUser = users.find((user) => String(user.id) === String(selectedUserId));

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Red</p>
          <h2>Mapa de {selectedBank.label}</h2>
        </div>
        <p className="page-copy">
          Selecciona riesgo o cliente para aislar una subred y generar un reporte exportable.
        </p>
      </header>

      {error ? <p className="form-error">{error}</p> : null}

      <article className="panel">
        <div className="panel-header">
          <h3>Filtros</h3>
          <span>{selectedUser ? selectedUser.full_name : selectedBank.label}</span>
        </div>

        <div className="network-toolbar">
          <div className="segmented-control">
            {RISK_OPTIONS.map((risk) => (
              <button
                key={risk}
                type="button"
                className={`segment-button ${riskFilter === risk ? "active" : ""}`}
                onClick={() => setRiskFilter(risk)}
              >
                {riskLabel(risk)}
              </button>
            ))}
          </div>

          <div className="network-toolbar-fields">
            <label>
              Cliente
              <select
                value={selectedUserId}
                onChange={(event) => setSelectedUserId(event.target.value)}
              >
                <option value="">Toda la red</option>
                {users.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.full_name} · {user.email}
                  </option>
                ))}
              </select>
            </label>

            <button
              type="button"
              className="secondary-button"
              onClick={() => {
                setSelectedUserId("");
                setRiskFilter("all");
              }}
            >
              Limpiar
            </button>
          </div>
        </div>
      </article>

      <div className="metric-grid">
        <article className="metric-card">
          <span>Nodos visibles</span>
          <strong>{graph.nodes.length}</strong>
        </article>
        <article className="metric-card">
          <span>Enlaces visibles</span>
          <strong>{graph.edges.length}</strong>
        </article>
        <article className="metric-card">
          <span>Filtro activo</span>
          <strong>{riskLabel(riskFilter)}</strong>
        </article>
        <article className="metric-card accent">
          <span>Cliente enfocado</span>
          <strong>{selectedUser ? selectedUser.full_name : "Toda la red"}</strong>
        </article>
      </div>

      <article className="panel">
        <div className="panel-header">
          <h3>Graph view</h3>
          <span>{graphLoading ? "Actualizando..." : `${graph.nodes.length} nodos · ${graph.edges.length} enlaces`}</span>
        </div>

        <div className="graph-legend">
          <span><i className="legend-dot low" /> Low</span>
          <span><i className="legend-dot medium" /> Medium</span>
          <span><i className="legend-dot high" /> High</span>
        </div>

        <div className="graph-canvas dark">
          <ReactFlow nodes={graph.nodes} edges={graph.edges} fitView>
            <MiniMap />
            <Controls />
            <Background />
          </ReactFlow>
        </div>
      </article>

      <div className="two-column-grid">
        <article className="panel">
          <div className="panel-header">
            <h3>Reporte de cliente</h3>
            <span>{selectedUser ? "Exportable" : "Selecciona un cliente"}</span>
          </div>

          {!selectedUserId ? (
            <p className="empty-state">Selecciona un cliente para generar su reporte.</p>
          ) : reportLoading ? (
            <p className="empty-state">Generando reporte...</p>
          ) : report ? (
            <div className="report-section">
              <div className="report-grid">
                <div className="compact-metric">
                  <small>Transacciones</small>
                  <strong>{report.total_transactions}</strong>
                </div>
                <div className="compact-metric">
                  <small>Con alerta</small>
                  <strong>{report.flagged_transactions}</strong>
                </div>
                <div className="compact-metric">
                  <small>Enviado</small>
                  <strong>{formatCurrency(report.total_sent)}</strong>
                </div>
                <div className="compact-metric">
                  <small>Recibido</small>
                  <strong>{formatCurrency(report.total_received)}</strong>
                </div>
              </div>

              <div className="report-meta">
                <p><strong>Cliente:</strong> {report.user.full_name}</p>
                <p><strong>Email:</strong> {report.user.email}</p>
                <p><strong>Cuentas:</strong> {report.accounts.map((account) => account.account_number).join(", ")}</p>
                <p><strong>Contrapartes:</strong> {report.distinct_counterparties}</p>
                <p><strong>Distribución:</strong> low {report.low} · medium {report.medium} · high {report.high}</p>
                <p><strong>Generado:</strong> {formatDate(report.generated_at)}</p>
              </div>

              <button
                type="button"
                className="primary-button"
                onClick={() => downloadReport(report, selectedBank.label)}
              >
                Descargar reporte
              </button>
            </div>
          ) : (
            <p className="empty-state">No se pudo generar el reporte.</p>
          )}
        </article>

        <article className="panel">
          <div className="panel-header">
            <h3>Contrapartes frecuentes</h3>
            <span>{report?.top_counterparties?.length ?? 0} resultados</span>
          </div>
          {report?.top_counterparties?.length ? (
            <div className="detail-list">
              {report.top_counterparties.map((counterparty) => (
                <div className="detail-item" key={counterparty.user_id}>
                  <div>
                    <p>{counterparty.full_name}</p>
                    <span>{counterparty.email}</span>
                  </div>
                  <div className="detail-item-side">
                    <strong>{formatCurrency(counterparty.total_amount)}</strong>
                    <span>{counterparty.transaction_count} tx</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-state">
              {selectedUserId ? "No hay contrapartes para este filtro." : "Selecciona un cliente para ver contrapartes."}
            </p>
          )}
        </article>
      </div>

      <article className="panel">
        <div className="panel-header">
          <h3>Transacciones del cliente</h3>
          <span>{report?.recent_transactions?.length ?? 0} registros</span>
        </div>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Origen</th>
                <th>Destino</th>
                <th>Monto</th>
                <th>Riesgo</th>
                <th>Canal</th>
                <th>Ubicación</th>
                <th>Fecha</th>
              </tr>
            </thead>
            <tbody>
              {report?.recent_transactions?.map((transaction) => (
                <tr key={transaction.transaction_id}>
                  <td>#{transaction.transaction_id}</td>
                  <td>{transaction.source_label}</td>
                  <td>{transaction.destination_label}</td>
                  <td>{formatCurrency(transaction.amount)}</td>
                  <td><span className={`risk-pill ${transaction.risk}`}>{transaction.risk}</span></td>
                  <td>{transaction.channel}</td>
                  <td>{transaction.location}</td>
                  <td>{formatDate(transaction.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!report?.recent_transactions?.length ? (
            <p className="empty-state">
              {selectedUserId ? "No hay transacciones para este filtro." : "Selecciona un cliente para ver sus transacciones."}
            </p>
          ) : null}
        </div>
      </article>
    </section>
  );
}
