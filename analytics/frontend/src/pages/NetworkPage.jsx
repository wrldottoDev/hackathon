import { useCallback, useEffect, useState } from "react";
import {
  Controls,
  Handle,
  MiniMap,
  Position,
  ReactFlow,
  useEdgesState,
  useNodesState,
} from "@xyflow/react";
import { analyticsRequest, formatCurrency } from "../api";
import { useAnalysisAuth } from "../auth";

const RISK_COLOR = { high: "#ff7a59", medium: "#f7c14a", low: "#3fd0b8" };
const RISK_BG = {
  high: "rgba(255,122,89,0.12)",
  medium: "rgba(247,193,74,0.12)",
  low: "rgba(63,208,184,0.12)",
};
const RISK_ICON = { high: "⚠", medium: "◈", low: "◉" };
const RISK_LABEL = { high: "Alto", medium: "Medio", low: "Bajo" };

function splitAccountNumber(accountNumber) {
  const [prefix, suffix = ""] = accountNumber.split("-");
  return {
    prefix,
    suffix,
    compactSuffix: suffix ? suffix.slice(-6) : accountNumber.slice(-6),
  };
}

function polarToCartesian(cx, cy, radius, angle) {
  return {
    x: cx + Math.cos(angle) * radius,
    y: cy + Math.sin(angle) * radius,
  };
}

function AccountNode({ data }) {
  const color = RISK_COLOR[data.risk] ?? RISK_COLOR.low;
  const bg = RISK_BG[data.risk] ?? RISK_BG.low;

  return (
    <>
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />
      <div
        title={data.account}
        style={{
          width: 138,
          height: 138,
          borderRadius: "50%",
          padding: 14,
          display: "grid",
          placeItems: "center",
          textAlign: "center",
          background: `
            radial-gradient(circle at 30% 30%, rgba(255,255,255,0.14), transparent 24%),
            linear-gradient(160deg, #0b1d23 0%, #11272d 100%)
          `,
          border: `2px solid ${color}`,
          boxShadow: `0 0 22px ${color}30, inset 0 0 24px rgba(255,255,255,0.03)`,
          position: "relative",
        }}
      >
        <span
          style={{
            position: "absolute",
            inset: 7,
            borderRadius: "50%",
            border: `1px dashed ${color}55`,
          }}
        />
        <span
          style={{
            position: "absolute",
            top: -8,
            right: 12,
            background: bg,
            border: `1px solid ${color}`,
            borderRadius: 999,
            color,
            fontSize: 10,
            fontWeight: 700,
            letterSpacing: "0.06em",
            padding: "2px 8px",
            textTransform: "uppercase",
          }}
        >
          {RISK_ICON[data.risk]} {RISK_LABEL[data.risk]}
        </span>
        <div
          style={{
            display: "grid",
            gap: 4,
            alignItems: "center",
            justifyItems: "center",
          }}
        >
          <span
            style={{
              background: "rgba(255,255,255,0.08)",
              borderRadius: 999,
              padding: "4px 10px",
              fontSize: 10,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              color: "#9eb4b7",
            }}
          >
            {data.bank}
          </span>
          <strong
            style={{
              margin: 0,
              fontSize: 26,
              lineHeight: 1,
              letterSpacing: "-0.04em",
              color: "#f7fbfc",
            }}
          >
            {data.accountCompact}
          </strong>
          <span
            style={{
              margin: 0,
              fontFamily: "monospace",
              fontSize: 11,
              color: "#8ea5a8",
            }}
          >
            {data.account}
          </span>
          <span style={{ color, fontSize: 11, fontWeight: 700 }}>
            {data.txCount} tx
          </span>
        </div>
      </div>
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
    </>
  );
}

const NODE_TYPES = { account: AccountNode };

function layoutNodes(rawNodes) {
  if (!rawNodes.length) {
    return [];
  }

  const byBank = {};
  for (const node of rawNodes) {
    if (!byBank[node.bank_code]) {
      byBank[node.bank_code] = [];
    }
    byBank[node.bank_code].push(node);
  }

  const bankCodes = Object.keys(byBank).sort();
  const graphCenter = { x: 620, y: 420 };
  const bankOrbitRadius =
    bankCodes.length === 1 ? 0 : Math.max(260, 190 + bankCodes.length * 55);
  const nodeSize = 138;
  const nodesPerRing = 8;
  const result = [];

  bankCodes.forEach((bankCode, bankIndex) => {
    const bankNodes = byBank[bankCode]
      .slice()
      .sort(
        (left, right) =>
          right.transaction_count - left.transaction_count ||
          left.label.localeCompare(right.label),
      );

    const bankAngle =
      bankCodes.length === 1
        ? -Math.PI / 2
        : -Math.PI / 2 + (bankIndex * Math.PI * 2) / bankCodes.length;
    const bankCenter =
      bankCodes.length === 1
        ? graphCenter
        : polarToCartesian(graphCenter.x, graphCenter.y, bankOrbitRadius, bankAngle);

    bankNodes.forEach((node, index) => {
      const { compactSuffix } = splitAccountNumber(node.label);
      const ring = Math.floor(index / nodesPerRing);
      const ringStart = ring * nodesPerRing;
      const ringNodes = bankNodes.slice(ringStart, ringStart + nodesPerRing);
      const indexInRing = index - ringStart;
      const ringRadius = bankNodes.length === 1 ? 0 : 94 + ring * 82;
      const nodeAngle =
        bankNodes.length === 1
          ? -Math.PI / 2
          : -Math.PI / 2 + (indexInRing * Math.PI * 2) / ringNodes.length;
      const circularPoint =
        ringRadius === 0
          ? bankCenter
          : polarToCartesian(bankCenter.x, bankCenter.y, ringRadius, nodeAngle);

      result.push({
        id: node.id,
        type: "account",
        position: {
          x: circularPoint.x - nodeSize / 2,
          y: circularPoint.y - nodeSize / 2,
        },
        data: {
          account: node.label,
          accountCompact: compactSuffix,
          bank: bankCode,
          risk: node.risk,
          txCount: node.transaction_count,
        },
      });
    });
  });

  return result;
}

function buildEdges(rawEdges) {
  return rawEdges.map((edge, idx) => {
    const isHeavy = edge.count > 3;

    return {
      id: `e-${edge.source}-${edge.target}-${idx}`,
      source: edge.source,
      target: edge.target,
      type: "smoothstep",
      label: `${formatCurrency(edge.amount)} · ${edge.count} tx`,
      animated: edge.count > 1,
      pathOptions: { borderRadius: 56, offset: 18 },
      style: {
        stroke: isHeavy ? "#f7c14a" : "#5f7c80",
        strokeWidth: Math.min(1.5 + edge.count * 0.5, 6),
        strokeOpacity: 0.9,
      },
      labelStyle: {
        fill: isHeavy ? "#ffd978" : "#8ea5a8",
        fontSize: 10,
        fontWeight: 700,
      },
      labelBgStyle: {
        fill: "rgba(7,19,22,0.88)",
        borderRadius: 6,
      },
    };
  });
}

export default function NetworkPage() {
  const { apiKey } = useAnalysisAuth();
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const [bankFilter, setBankFilter] = useState("");
  const [riskFilter, setRiskFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState(false);
  const [error, setError] = useState("");
  const [lastFetch, setLastFetch] = useState(null);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const loadGraph = useCallback(() => {
    setLoading(true);
    setError("");
    analyticsRequest("/network/graph", { apiKey })
      .then((data) => {
        setGraph(data);
        setLastFetch(new Date());
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [apiKey]);

  useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  useEffect(() => {
    let filteredNodes = graph.nodes;
    if (bankFilter) {
      filteredNodes = filteredNodes.filter((node) => node.bank_code === bankFilter);
    }
    if (riskFilter) {
      filteredNodes = filteredNodes.filter((node) => node.risk === riskFilter);
    }

    const visibleIds = new Set(filteredNodes.map((node) => node.id));
    const filteredEdges = graph.edges.filter(
      (edge) => visibleIds.has(edge.source) && visibleIds.has(edge.target),
    );

    setNodes(layoutNodes(filteredNodes));
    setEdges(buildEdges(filteredEdges));
  }, [graph, bankFilter, riskFilter, setNodes, setEdges]);

  const handleFetchTransactions = () => {
    setFetching(true);
    setError("");
    analyticsRequest("/transactions/fetch", { apiKey })
      .then(() => loadGraph())
      .catch((err) => setError(err.message))
      .finally(() => setFetching(false));
  };

  const bankOptions = [...new Set(graph.nodes.map((node) => node.bank_code))].sort();
  const highCount = graph.nodes.filter((node) => node.risk === "high").length;
  const medCount = graph.nodes.filter((node) => node.risk === "medium").length;
  const lowCount = graph.nodes.filter((node) => node.risk === "low").length;
  const totalVolume = graph.edges.reduce((sum, edge) => sum + edge.amount, 0);

  const visibleNodes = nodes;
  const visibleEdges = edges;

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Red</p>
          <h2>Mapa de red transaccional</h2>
        </div>
        <p className="page-copy">
          Vista agregada del ecosistema. Filtra por banco o nivel de riesgo y revisa
          los clústeres circulares de transferencias.
        </p>
      </header>

      {error ? <p className="form-error">{error}</p> : null}

      <div className="metric-grid">
        <article className="metric-card">
          <span>Nodos visibles</span>
          <strong>{visibleNodes.length}</strong>
        </article>
        <article className="metric-card">
          <span>Volumen total</span>
          <strong>{formatCurrency(totalVolume)}</strong>
        </article>
        <article className="metric-card" style={{ borderColor: "rgba(255,122,89,0.3)" }}>
          <span style={{ color: "#ff7a59" }}>⚠ Riesgo alto</span>
          <strong style={{ color: "#ff7a59" }}>{highCount}</strong>
        </article>
        <article className="metric-card" style={{ borderColor: "rgba(247,193,74,0.3)" }}>
          <span style={{ color: "#f7c14a" }}>◈ Riesgo medio</span>
          <strong style={{ color: "#f7c14a" }}>{medCount}</strong>
        </article>
      </div>

      <article className="panel">
        <div className="panel-header">
          <h3>Filtros</h3>
          <span>
            {loading
              ? "Cargando…"
              : `${visibleNodes.length} nodos · ${visibleEdges.length} conexiones`}
          </span>
        </div>
        <div className="network-toolbar" style={{ gridTemplateColumns: "1fr 1fr 1fr auto auto" }}>
          <label>
            Banco
            <select value={bankFilter} onChange={(event) => setBankFilter(event.target.value)}>
              <option value="">Todos los bancos</option>
              {bankOptions.map((code) => (
                <option key={code} value={code}>
                  {code}
                </option>
              ))}
            </select>
          </label>
          <label>
            Riesgo
            <select value={riskFilter} onChange={(event) => setRiskFilter(event.target.value)}>
              <option value="">Todos los niveles</option>
              <option value="high">⚠ Alto</option>
              <option value="medium">◈ Medio</option>
              <option value="low">◉ Bajo</option>
            </select>
          </label>
          <div />
          <button
            type="button"
            className="secondary-button"
            style={{ alignSelf: "end" }}
            onClick={() => {
              setBankFilter("");
              setRiskFilter("");
            }}
          >
            Limpiar
          </button>
          <button
            type="button"
            className="primary-button"
            style={{ alignSelf: "end" }}
            onClick={handleFetchTransactions}
            disabled={fetching || loading}
          >
            {fetching ? "Capturando…" : "⟳ Capturar transferencias"}
          </button>
        </div>
        {lastFetch ? (
          <p style={{ margin: "10px 0 0", fontSize: "0.82rem", color: "#8ea5a8" }}>
            Última captura: {lastFetch.toLocaleTimeString()}
          </p>
        ) : null}
      </article>

      <div className="tag-list">
        {["high", "medium", "low"].map((level) => (
          <button
            key={level}
            type="button"
            onClick={() => setRiskFilter(riskFilter === level ? "" : level)}
            className="network-chip"
            style={{
              border: `1px solid ${RISK_COLOR[level]}`,
              background:
                riskFilter === level ? RISK_BG[level] : "rgba(255,255,255,0.04)",
              color: RISK_COLOR[level],
              cursor: "pointer",
              fontWeight: riskFilter === level ? 700 : 400,
            }}
          >
            <span>{RISK_ICON[level]}</span>
            <span>
              {RISK_LABEL[level]} —{" "}
              {level === "high" ? highCount : level === "medium" ? medCount : lowCount} nodos
            </span>
          </button>
        ))}
      </div>

      <article className="panel" style={{ padding: 0, overflow: "hidden" }}>
        <div className="panel-header" style={{ padding: "18px 22px 0" }}>
          <h3>Mapa de red</h3>
          <span>{visibleEdges.length} conexiones · clústeres circulares por banco</span>
        </div>
        <div className="graph-canvas dark circular" style={{ height: 680, borderRadius: 0 }}>
          {visibleNodes.length === 0 && !loading ? (
            <div
              style={{
                height: "100%",
                display: "grid",
                placeItems: "center",
                color: "#8ea5a8",
              }}
            >
              No hay nodos que coincidan con los filtros seleccionados.
            </div>
          ) : (
            <ReactFlow
              nodes={visibleNodes}
              edges={visibleEdges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              nodeTypes={NODE_TYPES}
              fitView
              fitViewOptions={{ padding: 0.16 }}
              nodesDraggable={false}
              nodesConnectable={false}
              elementsSelectable={false}
              proOptions={{ hideAttribution: true }}
            >
              <MiniMap
                nodeColor={(node) => RISK_COLOR[node.data?.risk] ?? "#3fd0b8"}
                maskColor="rgba(7,19,22,0.7)"
                style={{ background: "#0b1e24", border: "1px solid rgba(133,166,171,0.18)" }}
              />
              <Controls />
            </ReactFlow>
          )}
        </div>
      </article>

      <div className="two-column-grid">
        <article className="panel">
          <div className="panel-header">
            <h3>Cuentas más activas</h3>
            <span>Top 12 por transacciones</span>
          </div>
          <div className="detail-list">
            {graph.nodes
              .filter((node) => !bankFilter || node.bank_code === bankFilter)
              .filter((node) => !riskFilter || node.risk === riskFilter)
              .slice()
              .sort((left, right) => right.transaction_count - left.transaction_count)
              .slice(0, 12)
              .map((node) => (
                <div className="detail-item" key={node.id}>
                  <div>
                    <p style={{ fontFamily: "monospace", fontSize: "0.9rem" }}>{node.label}</p>
                    <span>{node.bank_code}</span>
                  </div>
                  <div className="detail-item-side">
                    <span
                      className={`risk-pill ${node.risk}`}
                      style={{ boxShadow: `0 0 8px ${RISK_COLOR[node.risk]}44` }}
                    >
                      {RISK_ICON[node.risk]} {node.risk}
                    </span>
                    <strong>{node.transaction_count} tx</strong>
                  </div>
                </div>
              ))}
            {graph.nodes.length === 0 ? (
              <p className="empty-state">No hay nodos para mostrar.</p>
            ) : null}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <h3>Flujos principales</h3>
            <span>Top por monto acumulado</span>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Origen</th>
                  <th>Destino</th>
                  <th>Monto</th>
                  <th>Tx</th>
                </tr>
              </thead>
              <tbody>
                {graph.edges
                  .filter((edge) => {
                    if (!bankFilter && !riskFilter) {
                      return true;
                    }
                    const srcNode = graph.nodes.find((node) => node.id === edge.source);
                    const dstNode = graph.nodes.find((node) => node.id === edge.target);
                    const bankOk =
                      !bankFilter ||
                      srcNode?.bank_code === bankFilter ||
                      dstNode?.bank_code === bankFilter;
                    const riskOk =
                      !riskFilter ||
                      srcNode?.risk === riskFilter ||
                      dstNode?.risk === riskFilter;
                    return bankOk && riskOk;
                  })
                  .slice()
                  .sort((left, right) => right.amount - left.amount)
                  .slice(0, 12)
                  .map((edge) => {
                    const srcNode = graph.nodes.find((node) => node.id === edge.source);
                    const isHigh = srcNode?.risk === "high";
                    return (
                      <tr key={`${edge.source}-${edge.target}`}>
                        <td style={{ fontFamily: "monospace", fontSize: "0.85rem" }}>
                          {edge.source}
                        </td>
                        <td style={{ fontFamily: "monospace", fontSize: "0.85rem" }}>
                          {edge.target}
                        </td>
                        <td
                          style={{
                            color: isHigh ? "#ff7a59" : "inherit",
                            fontWeight: isHigh ? 700 : 400,
                          }}
                        >
                          {formatCurrency(edge.amount)}
                        </td>
                        <td>{edge.count}</td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
            {graph.edges.length === 0 ? (
              <p className="empty-state">No hay conexiones visibles.</p>
            ) : null}
          </div>
        </article>
      </div>
    </section>
  );
}
