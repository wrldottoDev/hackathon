import { useState, useEffect, useRef, useCallback } from "react"
import {
  AlertTriangle, CheckCircle2, Clock, TrendingUp, Database,
  RefreshCw, ArrowLeft, ChevronDown, Network, ShieldAlert,
  FileSearch, CheckCheck, X, Filter, Zap
} from "lucide-react"
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell
} from "recharts"

// ── Config ─────────────────────────────────────────────────────────────────

const API = "/api"

const RISK = {
  escalate: { color: "var(--red)",    dim: "var(--red-dim)",    label: "ESCALAR", icon: ShieldAlert },
  high:     { color: "var(--orange)", dim: "var(--orange-dim)", label: "ALTO",    icon: AlertTriangle },
  medium:   { color: "var(--amber)",  dim: "var(--amber-dim)",  label: "MEDIO",   icon: TrendingUp },
  low:      { color: "var(--green)",  dim: "var(--green-dim)",  label: "BAJO",    icon: CheckCircle2 },
}

const STATUS_LABELS = {
  pending:   "Pendiente",
  reviewed:  "Revisado",
  escalated: "Escalado",
  dismissed: "Descartado",
}

// ── API helpers ─────────────────────────────────────────────────────────────

const http = {
  get:   (path)       => fetch(`${API}${path}`).then(r => r.json()),
  post:  (path, body) => fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  }).then(r => r.json()),
  patch: (path, body) => fetch(`${API}${path}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then(r => r.json()),
}

// ── Atoms ───────────────────────────────────────────────────────────────────

function Badge({ level }) {
  const cfg = RISK[level] || RISK.low
  return (
    <span style={{
      fontFamily: "var(--font-mono)",
      fontSize: 10,
      fontWeight: 500,
      letterSpacing: "0.08em",
      padding: "3px 8px",
      borderRadius: 3,
      background: cfg.dim,
      color: cfg.color,
      border: `1px solid ${cfg.color}30`,
    }}>
      {cfg.label}
    </span>
  )
}

function StatusBadge({ status }) {
  const colors = {
    pending:   ["var(--text2)",  "var(--surface3)"],
    reviewed:  ["var(--blue)",   "var(--blue-dim)"],
    escalated: ["var(--red)",    "var(--red-dim)"],
    dismissed: ["var(--muted)",  "var(--surface2)"],
  }
  const [color, bg] = colors[status] || colors.pending
  return (
    <span style={{
      fontFamily: "var(--font-mono)",
      fontSize: 10,
      padding: "3px 8px",
      borderRadius: 3,
      background: bg,
      color,
    }}>
      {STATUS_LABELS[status] || status}
    </span>
  )
}

function ScoreRing({ score, size = 72 }) {
  const level = score >= 75 ? "escalate" : score >= 50 ? "high" : score >= 25 ? "medium" : "low"
  const color = RISK[level].color
  const r = (size - 10) / 2
  const circ = 2 * Math.PI * r
  const offset = circ - (score / 100) * circ
  return (
    <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="var(--border2)" strokeWidth={5} />
        <circle
          cx={size/2} cy={size/2} r={r}
          fill="none"
          stroke={color}
          strokeWidth={5}
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 1s cubic-bezier(0.4,0,0.2,1)" }}
        />
      </svg>
      <div style={{
        position: "absolute", inset: 0,
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
      }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 16, fontWeight: 500, color, lineHeight: 1 }}>
          {Math.round(score)}
        </span>
        <span style={{ fontSize: 9, color: "var(--text2)", marginTop: 1 }}>/ 100</span>
      </div>
    </div>
  )
}

function Spinner({ size = 16 }) {
  return (
    <div style={{
      width: size, height: size,
      borderRadius: "50%",
      border: `2px solid var(--border2)`,
      borderTopColor: "var(--amber)",
      animation: "spin 0.7s linear infinite",
      flexShrink: 0,
    }} />
  )
}

function MonoLabel({ children, color }) {
  return (
    <span style={{
      fontFamily: "var(--font-mono)",
      fontSize: 11,
      color: color || "var(--text2)",
    }}>
      {children}
    </span>
  )
}

function Divider() {
  return <div style={{ height: 1, background: "var(--border)", margin: "20px 0" }} />
}

// ── Stat Card ───────────────────────────────────────────────────────────────

function StatCard({ icon: Icon, label, value, color, delay = 0 }) {
  return (
    <div className="anim-fade-up" style={{
      animationDelay: `${delay}ms`,
      background: "var(--surface)",
      border: "1px solid var(--border)",
      borderRadius: "var(--radius-lg)",
      padding: "18px 20px",
      display: "flex",
      alignItems: "center",
      gap: 16,
    }}>
      <div style={{
        width: 38, height: 38,
        borderRadius: "var(--radius)",
        background: color ? `${color}18` : "var(--surface2)",
        display: "flex", alignItems: "center", justifyContent: "center",
        flexShrink: 0,
      }}>
        <Icon size={18} color={color || "var(--text2)"} />
      </div>
      <div>
        <p style={{ fontSize: 11, color: "var(--text2)", marginBottom: 2 }}>{label}</p>
        <p style={{
          fontFamily: "var(--font-mono)",
          fontSize: 22,
          fontWeight: 500,
          color: color || "var(--text)",
          lineHeight: 1,
        }}>
          {value}
        </p>
      </div>
    </div>
  )
}

// ── Signal Row ──────────────────────────────────────────────────────────────

function SignalRow({ signal, index }) {
  const [animated, setAnimated] = useState(false)
  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 100 + index * 120)
    return () => clearTimeout(t)
  }, [index])

  const color = signal.triggered ? "var(--amber)" : "var(--muted)"
  const fill  = signal.triggered
    ? (signal.code === "S1" ? "var(--red)" : signal.code === "S2" ? "var(--orange)" : signal.code === "S3" ? "var(--amber)" : signal.code === "S4" ? "var(--blue)" : "var(--green)")
    : "var(--muted)"

  const pct = animated && signal.triggered ? 100 : 0

  return (
    <div style={{
      padding: "12px 0",
      borderBottom: "1px solid var(--border)",
      opacity: signal.triggered ? 1 : 0.5,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{
            fontFamily: "var(--font-mono)",
            fontSize: 10,
            padding: "2px 6px",
            borderRadius: 3,
            background: signal.triggered ? `${fill}22` : "var(--surface2)",
            color: fill,
            border: `1px solid ${fill}44`,
          }}>
            {signal.code}
          </span>
          <span style={{ fontSize: 13, color: signal.triggered ? "var(--text)" : "var(--text2)" }}>
            {signal.label}
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color }}>
            {signal.triggered ? `+${signal.weight}` : "—"} / {signal.weight}
          </span>
          {signal.triggered && (
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: fill }} />
          )}
        </div>
      </div>

      <div style={{ height: 3, background: "var(--border2)", borderRadius: 2, overflow: "hidden" }}>
        <div style={{
          height: "100%",
          width: `${pct}%`,
          background: fill,
          borderRadius: 2,
          transition: "width 0.8s cubic-bezier(0.4,0,0.2,1)",
        }} />
      </div>

      <p style={{
        fontFamily: "var(--font-mono)",
        fontSize: 10,
        color: "var(--text2)",
        marginTop: 5,
      }}>
        {signal.detail}
      </p>
    </div>
  )
}

// ── Graph View ──────────────────────────────────────────────────────────────

function GraphView({ accountId, onBack }) {
  const svgRef  = useRef(null)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    http.get(`/graph/${accountId}?depth=2`).then(d => {
      setData(d)
      setLoading(false)
    })
  }, [accountId])

  useEffect(() => {
    if (!data || !svgRef.current) return
    import("d3").then(d3 => {
      const svg   = d3.select(svgRef.current)
      const W     = svgRef.current.clientWidth  || 700
      const H     = svgRef.current.clientHeight || 500

      svg.selectAll("*").remove()

      const nodeColor = (n) => {
        if (n.risk_level === "escalate") return "var(--red)"
        if (n.risk_level === "high")     return "var(--orange)"
        if (n.risk_level === "medium")   return "var(--amber)"
        if (n.risk_level === "low")      return "var(--green)"
        return "var(--text2)"
      }

      const nodes = data.nodes.map(n => ({ ...n }))
      const links = data.edges.map(e => ({
        source: nodes.find(n => n.id === e.source),
        target: nodes.find(n => n.id === e.target),
        amount: e.amount,
      })).filter(l => l.source && l.target)

      const sim = d3.forceSimulation(nodes)
        .force("link",    d3.forceLink(links).distance(90).strength(0.5))
        .force("charge",  d3.forceManyBody().strength(-200))
        .force("center",  d3.forceCenter(W / 2, H / 2))
        .force("collide", d3.forceCollide(28))

      // Aristas
      const link = svg.append("g")
        .selectAll("line").data(links).join("line")
        .attr("stroke", "var(--border2)")
        .attr("stroke-width", d => Math.max(1, Math.min(4, d.amount / 500)))
        .attr("stroke-opacity", 0.6)

      // Nodos
      const node = svg.append("g")
        .selectAll("g").data(nodes).join("g")
        .call(d3.drag()
          .on("start", (event, d) => { if (!event.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y })
          .on("drag",  (event, d) => { d.fx = event.x; d.fy = event.y })
          .on("end",   (event, d) => { if (!event.active) sim.alphaTarget(0); d.fx = null; d.fy = null })
        )

      node.append("circle")
        .attr("r", d => d.id === accountId ? 20 : 14)
        .attr("fill",   d => `${nodeColor(d)}22`)
        .attr("stroke", d => nodeColor(d))
        .attr("stroke-width", d => d.id === accountId ? 2.5 : 1.5)

      node.append("text")
        .text(d => d.code)
        .attr("text-anchor", "middle")
        .attr("dy", "0.35em")
        .attr("fill", d => nodeColor(d))
        .attr("font-family", "var(--font-mono)")
        .attr("font-size", d => d.id === accountId ? 9 : 8)

      sim.on("tick", () => {
        link
          .attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y)
        node.attr("transform", d => `translate(${d.x},${d.y})`)
      })
    })
  }, [data, accountId])

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
        <button onClick={onBack} style={{
          display: "flex", alignItems: "center", gap: 6,
          color: "var(--text2)", fontSize: 13, padding: "6px 10px",
          border: "1px solid var(--border)", borderRadius: "var(--radius)",
          transition: "color 0.15s",
        }}>
          <ArrowLeft size={14} /> Volver al caso
        </button>
        <span style={{ color: "var(--text2)", fontSize: 13 }}>Grafo de relaciones</span>
      </div>

      {loading ? (
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
          <Spinner size={20} />
          <span style={{ color: "var(--text2)" }}>Cargando grafo…</span>
        </div>
      ) : (
        <div style={{
          flex: 1,
          background: "var(--surface)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-lg)",
          overflow: "hidden",
        }}>
          <svg ref={svgRef} width="100%" height="100%" style={{ display: "block" }} />
        </div>
      )}

      {data && (
        <div style={{ display: "flex", gap: 16, marginTop: 12 }}>
          {["escalate","high","medium","low"].map(level => (
            <div key={level} style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: RISK[level].color }} />
              <span style={{ fontSize: 11, color: "var(--text2)" }}>{RISK[level].label}</span>
            </div>
          ))}
          <span style={{ marginLeft: "auto", fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text2)" }}>
            {data.nodes.length} nodos · {data.edges.length} aristas
          </span>
        </div>
      )}
    </div>
  )
}

// ── Case Detail ─────────────────────────────────────────────────────────────

function CaseDetail({ caseId, onBack }) {
  const [cas, setCas]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [scoring, setScoring] = useState(false)
  const [saving,  setSaving]  = useState(false)
  const [note,    setNote]    = useState("")
  const [view,    setView]    = useState("detail") // "detail" | "graph"

  const load = useCallback(() => {
    setLoading(true)
    http.get(`/cases/${caseId}`).then(d => { setCas(d); setNote(d.analyst_note || ""); setLoading(false) })
  }, [caseId])

  useEffect(() => { load() }, [load])

  const rescore = async () => {
    setScoring(true)
    await http.post(`/analyze/${cas.account_id}`)
    await load()
    setScoring(false)
  }

  const updateStatus = async (status) => {
    setSaving(true)
    const updated = await http.patch(`/cases/${caseId}`, { status, analyst_note: note })
    setCas(updated)
    setSaving(false)
  }

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 300, gap: 10 }}>
      <Spinner size={20} />
      <span style={{ color: "var(--text2)" }}>Cargando caso…</span>
    </div>
  )

  if (view === "graph") {
    return (
      <div style={{ height: "calc(100vh - 80px)" }}>
        <GraphView accountId={cas.account_id} onBack={() => setView("detail")} />
      </div>
    )
  }

  const signalsMeta = [
    { code: "S1", label: "Depósitos pequeños múltiples", weight: 30, detail: "" },
    { code: "S2", label: "Remitentes múltiples",         weight: 25, detail: "" },
    { code: "S3", label: "Dispersión rápida de fondos",  weight: 20, detail: "" },
    { code: "S4", label: "Actividad nocturna",           weight: 15, detail: "" },
    { code: "S5", label: "Reincidencia relacional",      weight: 10, detail: "" },
  ]

  const triggeredSet = new Set(cas.signals)

  return (
    <div className="anim-fade-up">
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <button onClick={onBack} style={{
          display: "flex", alignItems: "center", gap: 6, fontSize: 13,
          color: "var(--text2)", padding: "7px 12px",
          border: "1px solid var(--border)", borderRadius: "var(--radius)",
        }}>
          <ArrowLeft size={14} /> Casos
        </button>
        <MonoLabel>{cas.ref}</MonoLabel>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          <button
            onClick={() => setView("graph")}
            style={{
              display: "flex", alignItems: "center", gap: 6, fontSize: 13,
              color: "var(--text2)", padding: "7px 12px",
              border: "1px solid var(--border)", borderRadius: "var(--radius)",
            }}
          >
            <Network size={14} /> Ver grafo
          </button>
          <button
            onClick={rescore}
            disabled={scoring}
            style={{
              display: "flex", alignItems: "center", gap: 6, fontSize: 13,
              color: "var(--amber)", padding: "7px 12px",
              border: "1px solid var(--amber)40", borderRadius: "var(--radius)",
              background: "var(--amber-dim)",
            }}
          >
            {scoring ? <Spinner size={14} /> : <RefreshCw size={14} />}
            Re-analizar
          </button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: 20 }}>
        {/* Left col */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Score header */}
          <div style={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-lg)",
            padding: "24px",
            display: "flex",
            alignItems: "center",
            gap: 24,
          }}>
            <ScoreRing score={cas.score} size={90} />
            <div style={{ flex: 1 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                <Badge level={cas.risk_level} />
                <StatusBadge status={cas.status} />
              </div>
              <p style={{ fontSize: 13, color: "var(--text2)", lineHeight: 1.6 }}>{cas.summary}</p>
            </div>
          </div>

          {/* Señales */}
          <div style={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-lg)",
            padding: "20px 24px",
          }}>
            <p style={{ fontSize: 11, color: "var(--text2)", letterSpacing: "0.08em", marginBottom: 4 }}>
              SEÑALES EVALUADAS
            </p>
            {signalsMeta.map((s, i) => (
              <SignalRow
                key={s.code}
                index={i}
                signal={{
                  ...s,
                  triggered: triggeredSet.has(s.label),
                  score_added: triggeredSet.has(s.label) ? s.weight : 0,
                  detail: "",
                }}
              />
            ))}
          </div>
        </div>

        {/* Right col */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Recomendación */}
          <div style={{
            background: "var(--surface)",
            border: `1px solid ${RISK[cas.risk_level]?.color || "var(--border)"}40`,
            borderRadius: "var(--radius-lg)",
            padding: "18px 20px",
          }}>
            <p style={{ fontSize: 11, color: "var(--text2)", letterSpacing: "0.08em", marginBottom: 10 }}>
              RECOMENDACIÓN
            </p>
            <p style={{
              fontSize: 13,
              color: RISK[cas.risk_level]?.color || "var(--text)",
              lineHeight: 1.6,
            }}>
              {cas.recommendation}
            </p>
          </div>

          {/* Info del caso */}
          <div style={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-lg)",
            padding: "18px 20px",
          }}>
            <p style={{ fontSize: 11, color: "var(--text2)", letterSpacing: "0.08em", marginBottom: 12 }}>
              DETALLE DEL CASO
            </p>
            {[
              ["Cuenta",    cas.account_id.slice(0, 8) + "…"],
              ["Creado",    new Date(cas.created_at).toLocaleString("es-CR")],
              ["Revisado",  cas.reviewed_at ? new Date(cas.reviewed_at).toLocaleString("es-CR") : "—"],
            ].map(([k, v]) => (
              <div key={k} style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                <span style={{ fontSize: 12, color: "var(--text2)" }}>{k}</span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 11 }}>{v}</span>
              </div>
            ))}
          </div>

          {/* Acción del analista */}
          {cas.status === "pending" && (
            <div style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-lg)",
              padding: "18px 20px",
            }}>
              <p style={{ fontSize: 11, color: "var(--text2)", letterSpacing: "0.08em", marginBottom: 12 }}>
                DECISIÓN DEL ANALISTA
              </p>
              <textarea
                value={note}
                onChange={e => setNote(e.target.value)}
                placeholder="Notas opcionales…"
                style={{
                  width: "100%", height: 80, resize: "none",
                  background: "var(--surface2)", border: "1px solid var(--border)",
                  borderRadius: "var(--radius)", color: "var(--text)",
                  fontSize: 12, padding: "10px 12px",
                  fontFamily: "var(--font-mono)",
                  marginBottom: 12,
                }}
              />
              <div style={{ display: "flex", gap: 8, flexDirection: "column" }}>
                <button onClick={() => updateStatus("reviewed")} disabled={saving} style={{
                  display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
                  padding: "9px 0", borderRadius: "var(--radius)",
                  background: "var(--blue-dim)", color: "var(--blue)",
                  border: "1px solid var(--blue)40", fontSize: 12,
                }}>
                  {saving ? <Spinner size={12} /> : <CheckCheck size={14} />} Marcar revisado
                </button>
                <button onClick={() => updateStatus("escalated")} disabled={saving} style={{
                  display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
                  padding: "9px 0", borderRadius: "var(--radius)",
                  background: "var(--red-dim)", color: "var(--red)",
                  border: "1px solid var(--red)40", fontSize: 12,
                }}>
                  <ShieldAlert size={14} /> Escalar caso
                </button>
                <button onClick={() => updateStatus("dismissed")} disabled={saving} style={{
                  display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
                  padding: "9px 0", borderRadius: "var(--radius)",
                  background: "var(--surface2)", color: "var(--text2)",
                  border: "1px solid var(--border)", fontSize: 12,
                }}>
                  <X size={14} /> Descartar
                </button>
              </div>
            </div>
          )}

          {cas.status !== "pending" && cas.analyst_note && (
            <div style={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-lg)",
              padding: "16px 20px",
            }}>
              <p style={{ fontSize: 11, color: "var(--text2)", letterSpacing: "0.08em", marginBottom: 8 }}>
                NOTA DEL ANALISTA
              </p>
              <p style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text)", lineHeight: 1.6 }}>
                {cas.analyst_note}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Dashboard ───────────────────────────────────────────────────────────────

function Dashboard({ onSelect }) {
  const [stats,   setStats]   = useState(null)
  const [cases,   setCases]   = useState([])
  const [loading, setLoading] = useState(true)
  const [seeding, setSeeding] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [filter,  setFilter]  = useState({ risk: "", status: "" })

  const load = useCallback(async () => {
    setLoading(true)
    const [s, c] = await Promise.all([
      http.get("/dashboard"),
      http.get("/cases"),
    ])
    setStats(s)
    setCases(c)
    setLoading(false)
  }, [])

  useEffect(() => { load() }, [load])

  const seed = async () => {
    setSeeding(true)
    await http.post("/seed")
    await load()
    setSeeding(false)
  }

  const analyze = async () => {
    setAnalyzing(true)
    await http.post("/analyze/batch")
    await load()
    setAnalyzing(false)
  }

  const filtered = cases.filter(c =>
    (!filter.risk   || c.risk_level === filter.risk) &&
    (!filter.status || c.status     === filter.status)
  )

  const chartData = ["escalate","high","medium","low"].map(level => ({
    name: RISK[level].label,
    value: cases.filter(c => c.risk_level === level).length,
    color: RISK[level].color,
  }))

  return (
    <div>
      {/* Stat cards */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
        gap: 12,
        marginBottom: 24,
      }}>
        <StatCard icon={FileSearch}   label="Casos totales"  value={stats?.total_cases ?? "—"}    delay={0}   />
        <StatCard icon={Clock}        label="Pendientes"     value={stats?.pending      ?? "—"}    delay={60}  color="var(--amber)"  />
        <StatCard icon={AlertTriangle}label="Alto riesgo"    value={stats?.high_risk    ?? "—"}    delay={120} color="var(--orange)" />
        <StatCard icon={ShieldAlert}  label="Escalados"      value={stats?.escalated    ?? "—"}    delay={180} color="var(--red)"    />
        <StatCard icon={TrendingUp}   label="Score promedio" value={stats?.avg_score    ?? "—"}    delay={240} color="var(--blue)"   />
      </div>

      {/* Chart + Controls row */}
      <div style={{ display: "grid", gridTemplateColumns: "240px 1fr", gap: 16, marginBottom: 20 }}>
        {/* Mini bar chart */}
        <div style={{
          background: "var(--surface)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-lg)",
          padding: "16px 18px",
        }}>
          <p style={{ fontSize: 11, color: "var(--text2)", letterSpacing: "0.08em", marginBottom: 12 }}>
            DISTRIBUCIÓN DE RIESGO
          </p>
          <ResponsiveContainer width="100%" height={100}>
            <BarChart data={chartData} barSize={28}>
              <XAxis dataKey="name" tick={{ fontSize: 9, fill: "var(--text2)", fontFamily: "var(--font-mono)" }} axisLine={false} tickLine={false} />
              <YAxis hide />
              <Tooltip
                contentStyle={{ background: "var(--surface2)", border: "1px solid var(--border)", borderRadius: 6, fontSize: 11 }}
                labelStyle={{ color: "var(--text2)" }}
                itemStyle={{ color: "var(--text)" }}
              />
              <Bar dataKey="value" radius={3}>
                {chartData.map((d, i) => <Cell key={i} fill={d.color} fillOpacity={0.8} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Filters + Actions */}
        <div style={{
          background: "var(--surface)",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-lg)",
          padding: "16px 18px",
          display: "flex",
          flexDirection: "column",
          gap: 12,
        }}>
          <p style={{ fontSize: 11, color: "var(--text2)", letterSpacing: "0.08em" }}>FILTROS & ACCIONES</p>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
            <select value={filter.risk} onChange={e => setFilter(f => ({ ...f, risk: e.target.value }))}>
              <option value="">Todos los niveles</option>
              {Object.entries(RISK).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
            </select>
            <select value={filter.status} onChange={e => setFilter(f => ({ ...f, status: e.target.value }))}>
              <option value="">Todos los estados</option>
              {Object.entries(STATUS_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
            <div style={{ flex: 1 }} />
            <button
              onClick={seed}
              disabled={seeding}
              style={{
                display: "flex", alignItems: "center", gap: 6, padding: "8px 14px",
                border: "1px solid var(--border2)", borderRadius: "var(--radius)",
                color: "var(--text2)", fontSize: 12,
              }}
            >
              {seeding ? <Spinner size={13} /> : <Database size={13} />}
              Generar datos
            </button>
            <button
              onClick={analyze}
              disabled={analyzing || cases.length === 0}
              style={{
                display: "flex", alignItems: "center", gap: 6, padding: "8px 14px",
                border: "1px solid var(--amber)50", borderRadius: "var(--radius)",
                background: "var(--amber-dim)", color: "var(--amber)", fontSize: 12,
              }}
            >
              {analyzing ? <Spinner size={13} /> : <Zap size={13} />}
              Analizar todo
            </button>
          </div>
        </div>
      </div>

      {/* Cases table */}
      <div style={{
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-lg)",
        overflow: "hidden",
      }}>
        <div style={{ padding: "14px 20px", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <p style={{ fontSize: 11, color: "var(--text2)", letterSpacing: "0.08em" }}>
            ALERTAS — {filtered.length} caso{filtered.length !== 1 ? "s" : ""}
          </p>
          <button onClick={load} style={{ color: "var(--text2)", display: "flex", alignItems: "center", gap: 4, fontSize: 12 }}>
            {loading ? <Spinner size={12} /> : <RefreshCw size={12} />}
          </button>
        </div>

        {loading && cases.length === 0 ? (
          <div style={{ padding: 40, textAlign: "center", color: "var(--text2)" }}>Cargando casos…</div>
        ) : filtered.length === 0 ? (
          <div style={{ padding: 40, textAlign: "center", color: "var(--text2)" }}>
            {cases.length === 0 ? "Genera datos y ejecuta el análisis para ver casos." : "Sin resultados para los filtros aplicados."}
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  {["Referencia","Cuenta","Score","Riesgo","Señales","Estado","Creado",""].map(h => (
                    <th key={h} style={{
                      padding: "10px 16px", textAlign: "left",
                      fontSize: 10, color: "var(--text2)",
                      letterSpacing: "0.07em", fontWeight: 500,
                      fontFamily: "var(--font-mono)",
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map((c, i) => (
                  <tr
                    key={c.id}
                    className="anim-fade-up"
                    style={{
                      animationDelay: `${i * 30}ms`,
                      borderBottom: "1px solid var(--border)",
                      cursor: "pointer",
                      transition: "background 0.1s",
                    }}
                    onMouseEnter={e => e.currentTarget.style.background = "var(--surface2)"}
                    onMouseLeave={e => e.currentTarget.style.background = "transparent"}
                    onClick={() => onSelect(c.id)}
                  >
                    <td style={{ padding: "12px 16px" }}>
                      <MonoLabel color="var(--text)">{c.ref}</MonoLabel>
                    </td>
                    <td style={{ padding: "12px 16px" }}>
                      <MonoLabel>{c.account_id.slice(0, 8)}…</MonoLabel>
                    </td>
                    <td style={{ padding: "12px 16px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <ScoreRing score={c.score} size={36} />
                      </div>
                    </td>
                    <td style={{ padding: "12px 16px" }}>
                      <Badge level={c.risk_level} />
                    </td>
                    <td style={{ padding: "12px 16px" }}>
                      <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                        {c.signals.slice(0, 3).map(s => (
                          <span key={s} style={{
                            fontFamily: "var(--font-mono)", fontSize: 10,
                            padding: "2px 6px", borderRadius: 3,
                            background: "var(--amber-dim)", color: "var(--amber)",
                          }}>
                            {s.split(" ")[0]}
                          </span>
                        ))}
                        {c.signals.length > 3 && (
                          <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text2)" }}>
                            +{c.signals.length - 3}
                          </span>
                        )}
                      </div>
                    </td>
                    <td style={{ padding: "12px 16px" }}>
                      <StatusBadge status={c.status} />
                    </td>
                    <td style={{ padding: "12px 16px" }}>
                      <MonoLabel>{new Date(c.created_at).toLocaleDateString("es-CR")}</MonoLabel>
                    </td>
                    <td style={{ padding: "12px 16px" }}>
                      <ChevronDown size={14} color="var(--text2)" style={{ transform: "rotate(-90deg)" }} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

// ── App Shell ───────────────────────────────────────────────────────────────

export default function App() {
  const [view,     setView]    = useState("dashboard")
  const [caseId,   setCaseId]  = useState(null)

  const selectCase = (id) => { setCaseId(id); setView("case") }
  const goBack     = ()    => { setView("dashboard") }

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Top nav */}
      <header style={{
        background: "var(--surface)",
        borderBottom: "1px solid var(--border)",
        padding: "0 32px",
        height: 56,
        display: "flex",
        alignItems: "center",
        gap: 24,
        position: "sticky",
        top: 0,
        zIndex: 100,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 28, height: 28,
            borderRadius: 6,
            background: "var(--amber-dim)",
            border: "1px solid var(--amber)50",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <Network size={14} color="var(--amber)" />
          </div>
          <span style={{ fontWeight: 700, fontSize: 15, letterSpacing: "0.04em" }}>NEXO</span>
          <span style={{ color: "var(--text2)", fontWeight: 400 }}>Risk</span>
        </div>

        <div style={{ width: 1, height: 20, background: "var(--border)" }} />

        <nav style={{ display: "flex", gap: 4 }}>
          {[
            { id: "dashboard", label: "Dashboard" },
          ].map(item => (
            <button
              key={item.id}
              onClick={() => { setView(item.id); setCaseId(null) }}
              style={{
                fontSize: 13, padding: "6px 12px", borderRadius: "var(--radius)",
                color: view === item.id ? "var(--text)" : "var(--text2)",
                background: view === item.id ? "var(--surface2)" : "transparent",
              }}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{
            width: 7, height: 7, borderRadius: "50%",
            background: "var(--green)",
            animation: "pulse 2s ease-in-out infinite",
          }} />
          <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text2)" }}>
            API conectada
          </span>
        </div>
      </header>

      {/* Main */}
      <main style={{ flex: 1, padding: "28px 32px", maxWidth: 1280, width: "100%", margin: "0 auto" }}>
        {view === "dashboard" && <Dashboard onSelect={selectCase} />}
        {view === "case"      && <CaseDetail caseId={caseId} onBack={goBack} />}
      </main>

      {/* Footer */}
      <footer style={{ padding: "12px 32px", borderTop: "1px solid var(--border)", display: "flex", justifyContent: "space-between" }}>
        <MonoLabel>NEXO Risk v1.0 — Hackathon Rastrea la Red</MonoLabel>
        <MonoLabel>La decisión final es siempre humana.</MonoLabel>
      </footer>
    </div>
  )
}
