import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Background, Controls, MiniMap, ReactFlow } from "@xyflow/react";
import { analyticsRequest, formatCurrency } from "../api";
import { useAnalysisAuth } from "../auth";

const RISK_COLOR = {
  high: "#ff6b6b",
  medium: "#f4b740",
  low: "#29c3a5",
};

const RISK_ICON = {
  high: "⚠",
  medium: "◈",
  low: "◉",
};

const RISK_LABEL = {
  high: "Alto",
  medium: "Medio",
  low: "Bajo",
};

function compactAccount(accountNumber) {
  const [bankCode, suffix = ""] = accountNumber.split("-");
  const compactSuffix = suffix ? suffix.slice(-6) : accountNumber.slice(-6);
  return `${bankCode} · ${compactSuffix}`;
}

function riskColor(risk) {
  return RISK_COLOR[risk] ?? RISK_COLOR.low;
}

function riskLabel(risk) {
  if (!risk) {
    return "Todos";
  }
  return `${RISK_ICON[risk]} ${RISK_LABEL[risk]}`;
}

function maxRisk(...risks) {
  if (risks.includes("high")) {
    return "high";
  }
  if (risks.includes("medium")) {
    return "medium";
  }
  return "low";
}

function getEdgeId(edge, index) {
  return edge.id ?? `edge-${edge.source}-${edge.target}-${index}`;
}

function buildFlow(graph, highlightNodeIds, highlightEdgeIds) {
  const hasHighlight = highlightNodeIds && highlightNodeIds.size > 0;
  const centerX = 620;
  const centerY = 350;
  const sortedNodes = graph.nodes
    .slice()
    .sort(
      (left, right) =>
        right.transaction_count - left.transaction_count ||
        left.label.localeCompare(right.label),
    );

  const total = Math.max(sortedNodes.length, 1);
  const radius = Math.max(260, total * 18);
  const nodes = sortedNodes.map((node, index) => {
    const angle = (Math.PI * 2 * index) / total;
    const isLit = !hasHighlight || highlightNodeIds.has(node.id);
    const color = riskColor(node.risk);

    return {
      id: node.id,
      position: {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
      },
      data: {
        label: `${compactAccount(node.label)} · ${node.transaction_count} tx`,
      },
      style: {
        background: isLit ? "#102126" : "rgba(16,33,38,0.3)",
        border: `2px solid ${isLit ? color : "rgba(133,166,171,0.15)"}`,
        borderRadius: "18px",
        color: isLit ? "#f7fbfc" : "rgba(247,251,252,0.25)",
        width: 220,
        padding: "14px",
        fontSize: "12px",
        boxShadow: isLit && hasHighlight ? `0 0 18px ${color}66` : "none",
        transition: "all 260ms ease",
        zIndex: isLit ? 10 : 1,
      },
    };
  });

  const riskByNodeId = Object.fromEntries(
    graph.nodes.map((node) => [node.id, node.risk]),
  );

  const edges = graph.edges.map((edge, index) => {
    const edgeId = getEdgeId(edge, index);
    const edgeRisk = maxRisk(riskByNodeId[edge.source], riskByNodeId[edge.target]);
    const isLit = !hasHighlight || (highlightEdgeIds && highlightEdgeIds.has(edgeId));

    return {
      id: edgeId,
      source: edge.source,
      target: edge.target,
      label: formatCurrency(edge.amount),
      animated: isLit && edgeRisk !== "low",
      style: {
        stroke: isLit ? riskColor(edgeRisk) : "rgba(133,166,171,0.12)",
        strokeWidth: isLit
          ? edgeRisk === "high" ? 3.4 : edgeRisk === "medium" ? 2.6 : 1.8
          : 1,
        filter: isLit && hasHighlight ? `drop-shadow(0 0 6px ${riskColor(edgeRisk)}88)` : "none",
        transition: "all 260ms ease",
      },
      labelStyle: {
        fill: isLit ? "#c8dfe0" : "rgba(142,165,168,0.2)",
        fontSize: 11,
        fontWeight: 600,
      },
    };
  });

  return { nodes, edges };
}

export default function NetworkPage() {
  const { apiKey } = useAnalysisAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState(false);
  const [error, setError] = useState("");
  const [lastFetch, setLastFetch] = useState(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState(null);

  const bankFilter = searchParams.get("bank") || "";
  const riskFilter = searchParams.get("risk") || "";
  const selectedAccount = searchParams.get("account") || "";

  const updateSearchParams = useCallback(
    (patch) => {
      const next = new URLSearchParams(searchParams);
      Object.entries(patch).forEach(([key, value]) => {
        if (value) {
          next.set(key, value);
        } else {
          next.delete(key);
        }
      });
      setSearchParams(next, { replace: true });
    },
    [searchParams, setSearchParams],
  );

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

  const filteredGraph = useMemo(() => {
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

    return {
      nodes: filteredNodes,
      edges: filteredEdges,
    };
  }, [graph, bankFilter, riskFilter]);

  useEffect(() => {
    if (
      selectedAccount &&
      !filteredGraph.nodes.some((node) => node.id === selectedAccount)
    ) {
      updateSearchParams({ account: "" });
    }
  }, [selectedAccount, filteredGraph.nodes, updateSearchParams]);

  useEffect(() => {
    if (
      selectedEdgeId &&
      !filteredGraph.edges.some((edge, index) => getEdgeId(edge, index) === selectedEdgeId)
    ) {
      setSelectedEdgeId(null);
    }
  }, [filteredGraph.edges, selectedEdgeId]);

  const { highlightNodeIds, highlightEdgeIds } = useMemo(() => {
    if (!selectedAccount && !selectedEdgeId) {
      return { highlightNodeIds: null, highlightEdgeIds: null };
    }

    const nodeIds = new Set();
    const edgeIds = new Set();

    if (selectedAccount) {
      nodeIds.add(selectedAccount);
      filteredGraph.edges.forEach((edge, index) => {
        const edgeId = getEdgeId(edge, index);
        if (edge.source === selectedAccount || edge.target === selectedAccount) {
          edgeIds.add(edgeId);
          nodeIds.add(edge.source);
          nodeIds.add(edge.target);
        }
      });
    }

    if (selectedEdgeId) {
      filteredGraph.edges.forEach((edge, index) => {
        const edgeId = getEdgeId(edge, index);
        if (edgeId === selectedEdgeId) {
          edgeIds.add(edgeId);
          nodeIds.add(edge.source);
          nodeIds.add(edge.target);
        }
      });
    }

    return { highlightNodeIds: nodeIds, highlightEdgeIds: edgeIds };
  }, [filteredGraph, selectedAccount, selectedEdgeId]);

  const flowGraph = useMemo(
    () => buildFlow(filteredGraph, highlightNodeIds, highlightEdgeIds),
    [filteredGraph, highlightNodeIds, highlightEdgeIds],
  );

  const selectedNode = filteredGraph.nodes.find((node) => node.id === selectedAccount) || null;
  const selectedConnections = filteredGraph.edges
    .filter(
      (edge) => edge.source === selectedAccount || edge.target === selectedAccount,
    )
    .slice()
    .sort((left, right) => right.amount - left.amount)
    .slice(0, 6);
  const selectedEdge = filteredGraph.edges.find(
    (edge, index) => getEdgeId(edge, index) === selectedEdgeId,
  );

  const bankOptions = useMemo(
    () => [...new Set(graph.nodes.map((node) => node.bank_code))].sort(),
    [graph.nodes],
  );

  const highCount = filteredGraph.nodes.filter((node) => node.risk === "high").length;
  const medCount = filteredGraph.nodes.filter((node) => node.risk === "medium").length;
  const lowCount = filteredGraph.nodes.filter((node) => node.risk === "low").length;
  const totalVolume = filteredGraph.edges.reduce((sum, edge) => sum + edge.amount, 0);
  const activeFilterTags = [
    bankFilter ? `Banco: ${bankFilter}` : null,
    riskFilter ? `Riesgo: ${riskFilter}` : null,
    selectedAccount ? `Cuenta foco: ${selectedAccount}` : null,
  ].filter(Boolean);

  const handleFetchTransactions = () => {
    setFetching(true);
    setError("");
    analyticsRequest("/transactions/fetch", { apiKey })
      .then(() => loadGraph())
      .catch((err) => setError(err.message))
      .finally(() => setFetching(false));
  };

  const onNodeClick = useCallback(
    (_event, node) => {
      setSelectedEdgeId(null);
      updateSearchParams({
        account: selectedAccount === node.id ? "" : node.id,
      });
    },
    [selectedAccount, updateSearchParams],
  );

  const onEdgeClick = useCallback((_event, edge) => {
    setSelectedEdgeId((prev) => (prev === edge.id ? null : edge.id));
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedEdgeId(null);
    if (selectedAccount) {
      updateSearchParams({ account: "" });
    }
  }, [selectedAccount, updateSearchParams]);

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Red</p>
          <h2>Mapa de red transaccional</h2>
        </div>
        <p className="page-copy">
          Vista agregada del ecosistema. Filtra por banco o nivel de riesgo y usa el
          foco por cuenta para seguir relaciones y saltar al follow-up.
        </p>
      </header>

      {error ? <p className="form-error">{error}</p> : null}

      <div className="metric-grid">
        <article className="metric-card">
          <span>Nodos visibles</span>
          <strong>{filteredGraph.nodes.length}</strong>
        </article>
        <article className="metric-card">
          <span>Enlaces visibles</span>
          <strong>{filteredGraph.edges.length}</strong>
        </article>
        <article className="metric-card">
          <span>Filtro activo</span>
          <strong>{riskLabel(riskFilter)}</strong>
        </article>
        <article className="metric-card accent">
          <span>Volumen visible</span>
          <strong>{formatCurrency(totalVolume)}</strong>
        </article>
      </div>

      <article className="panel">
        <div className="panel-header">
          <h3>Filtros</h3>
          <span>
            {loading
              ? "Cargando..."
              : `${filteredGraph.nodes.length} nodos · ${filteredGraph.edges.length} enlaces`}
          </span>
        </div>
        <div
          className="network-toolbar"
          style={{ gridTemplateColumns: "1fr 1fr 1fr auto auto" }}
        >
          <label>
            Banco
            <select
              value={bankFilter}
              onChange={(event) => updateSearchParams({ bank: event.target.value })}
            >
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
            <select
              value={riskFilter}
              onChange={(event) => updateSearchParams({ risk: event.target.value })}
            >
              <option value="">Todos los niveles</option>
              <option value="high">⚠ Alto</option>
              <option value="medium">◈ Medio</option>
              <option value="low">◉ Bajo</option>
            </select>
          </label>
          <div className="active-filters" style={{ alignSelf: "end" }}>
            {activeFilterTags.length ? (
              activeFilterTags.map((tag) => <span key={tag} className="active-filter-tag">{tag}</span>)
            ) : (
              <span className="active-filter-tag">Sin filtros activos</span>
            )}
          </div>
          <button
            type="button"
            className="secondary-button"
            style={{ alignSelf: "end" }}
            onClick={() => {
              setSelectedEdgeId(null);
              setSearchParams({}, { replace: true });
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
            {fetching ? "Capturando..." : "⟳ Capturar transferencias"}
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
            onClick={() =>
              updateSearchParams({ risk: riskFilter === level ? "" : level })
            }
            className="network-chip"
            style={{
              border: `1px solid ${RISK_COLOR[level]}`,
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

      <article className="panel">
        <div className="panel-header">
          <h3>Graph view</h3>
          <span>
            {loading
              ? "Actualizando..."
              : `${flowGraph.nodes.length} nodos · ${flowGraph.edges.length} enlaces`}
          </span>
        </div>

        <div className="graph-legend">
          <span>
            <i className="legend-dot low" /> Low
          </span>
          <span>
            <i className="legend-dot medium" /> Medium
          </span>
          <span>
            <i className="legend-dot high" /> High
          </span>
        </div>

        <div className="graph-canvas dark">
          {flowGraph.nodes.length === 0 && !loading ? (
            <div
              className="empty-state"
              style={{
                height: "100%",
                display: "grid",
                placeItems: "center",
                margin: 0,
                borderRadius: 0,
              }}
            >
              No hay nodos que coincidan con los filtros seleccionados.
            </div>
          ) : (
            <ReactFlow
              nodes={flowGraph.nodes}
              edges={flowGraph.edges}
              fitView
              nodesDraggable={false}
              nodesConnectable={false}
              elementsSelectable
              onNodeClick={onNodeClick}
              onEdgeClick={onEdgeClick}
              onPaneClick={onPaneClick}
              proOptions={{ hideAttribution: true }}
            >
              <MiniMap />
              <Controls />
              <Background />
            </ReactFlow>
          )}
        </div>
      </article>

      <article className="panel">
        <div className="panel-header">
          <h3>Contexto seleccionado</h3>
          <span>
            {selectedNode
              ? selectedNode.label
              : selectedEdge
                ? `${selectedEdge.source} → ${selectedEdge.target}`
                : "Sin foco activo"}
          </span>
        </div>

        {selectedNode ? (
          <div className="context-grid">
            <div className="context-card">
              <small>Cuenta enfocada</small>
              <strong className="mono">{selectedNode.label}</strong>
              <p>
                Banco {selectedNode.bank_code} · Riesgo {riskLabel(selectedNode.risk)} ·{" "}
                {selectedNode.transaction_count} transacciones visibles.
              </p>
              <div className="panel-actions">
                <Link
                  className="inline-link-button"
                  to={`/follow-up?account=${encodeURIComponent(selectedNode.label)}`}
                >
                  Abrir follow-up
                </Link>
                <Link
                  className="inline-link-button"
                  to={`/alerts?account=${encodeURIComponent(selectedNode.label)}`}
                >
                  Ver alertas de la cuenta
                </Link>
              </div>
            </div>
            <div className="context-card">
              <small>Contrapartes visibles</small>
              <div className="detail-list">
                {selectedConnections.map((edge) => {
                  const counterparty =
                    edge.source === selectedNode.label ? edge.target : edge.source;
                  return (
                    <div key={`${selectedNode.label}-${counterparty}`} className="detail-item">
                      <div>
                        <p>{counterparty}</p>
                        <span>{formatCurrency(edge.amount)} · {edge.count} tx</span>
                      </div>
                      <div className="detail-item-actions">
                        <button
                          type="button"
                          className="inline-link-button"
                          onClick={() => updateSearchParams({ account: counterparty })}
                        >
                          Enfocar
                        </button>
                        <Link
                          className="inline-link-button"
                          to={`/follow-up?account=${encodeURIComponent(counterparty)}`}
                        >
                          Follow-up
                        </Link>
                      </div>
                    </div>
                  );
                })}
                {!selectedConnections.length ? (
                  <p className="empty-state analytics-note">
                    La cuenta no tiene conexiones visibles bajo los filtros actuales.
                  </p>
                ) : null}
              </div>
            </div>
          </div>
        ) : selectedEdge ? (
          <div className="context-grid">
            <div className="context-card">
              <small>Enlace seleccionado</small>
              <strong className="mono">
                {selectedEdge.source} → {selectedEdge.target}
              </strong>
              <p>
                Flujo acumulado de {formatCurrency(selectedEdge.amount)} en {selectedEdge.count}{" "}
                transacciones visibles.
              </p>
            </div>
            <div className="context-card">
              <small>Acciones rápidas</small>
              <div className="panel-actions">
                <button
                  type="button"
                  className="inline-link-button"
                  onClick={() => updateSearchParams({ account: selectedEdge.source })}
                >
                  Enfocar origen
                </button>
                <button
                  type="button"
                  className="inline-link-button"
                  onClick={() => updateSearchParams({ account: selectedEdge.target })}
                >
                  Enfocar destino
                </button>
              </div>
            </div>
          </div>
        ) : (
          <p className="empty-state analytics-note">
            Haz click en una cuenta o un enlace del grafo para fijar contexto y abrir
            el siguiente paso de investigación.
          </p>
        )}
      </article>

      <div className="two-column-grid">
        <article className="panel">
          <div className="panel-header">
            <h3>Cuentas más activas</h3>
            <span>Top 12 por transacciones</span>
          </div>
          <div className="detail-list">
            {filteredGraph.nodes
              .slice()
              .sort((left, right) => right.transaction_count - left.transaction_count)
              .slice(0, 12)
              .map((node) => (
                <div className="detail-item" key={node.id}>
                  <div>
                    <p style={{ fontFamily: "monospace", fontSize: "0.9rem" }}>{node.label}</p>
                    <span>{node.bank_code}</span>
                    <div className="detail-item-actions">
                      <button
                        type="button"
                        className="inline-link-button"
                        onClick={() => updateSearchParams({ account: node.label })}
                      >
                        Enfocar
                      </button>
                      <Link
                        className="inline-link-button"
                        to={`/follow-up?account=${encodeURIComponent(node.label)}`}
                      >
                        Follow-up
                      </Link>
                    </div>
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
            {filteredGraph.nodes.length === 0 ? (
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
                  <th>Transacciones</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredGraph.edges
                  .slice()
                  .sort((left, right) => right.amount - left.amount)
                  .slice(0, 12)
                  .map((edge, index) => (
                    <tr key={`${edge.source}-${edge.target}-${index}`}>
                      <td style={{ fontFamily: "monospace" }}>{edge.source}</td>
                      <td style={{ fontFamily: "monospace" }}>{edge.target}</td>
                      <td>{formatCurrency(edge.amount)}</td>
                      <td>{edge.count}</td>
                      <td>
                        <div className="table-actions">
                          <button
                            type="button"
                            className="inline-link-button"
                            onClick={() => updateSearchParams({ account: edge.source })}
                          >
                            Enfocar origen
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
            {filteredGraph.edges.length === 0 ? (
              <p className="empty-state analytics-note">
                No hay conexiones suficientes para mostrar.
              </p>
            ) : null}
          </div>
        </article>
      </div>
    </section>
  );
}
