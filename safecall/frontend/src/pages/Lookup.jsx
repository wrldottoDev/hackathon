import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";
import Header from "../components/Header";
import RiskRing from "../components/RiskRing";
import Badge from "../components/Badge";

function normalizeLookupNumber(value) {
  const digits = value.replace(/\D/g, "");

  if (!digits) return "";
  if (digits.startsWith("506") && digits.length === 11) return `+${digits}`;
  if (digits.length === 8) return `+506${digits}`;

  return value.trim();
}

export default function Lookup() {
  const [searchParams] = useSearchParams();
  const [number, setNumber] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const runLookup = async (rawNumber) => {
    const normalizedNumber = normalizeLookupNumber(rawNumber);
    if (!normalizedNumber) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await api.lookup(normalizedNumber);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const queryNumber = searchParams.get("q");
    if (!queryNumber) return;
    setNumber(queryNumber);
    runLookup(queryNumber);
  }, [searchParams]);

  const handleSearch = async (e) => {
    e.preventDefault();
    await runLookup(number);
  };

  return (
    <div className="max-w-lg mx-auto">
      <Header title="SafeCall" subtitle="Consulta de numeros telefonicos" />

      <div className="px-4">
        <form onSubmit={handleSearch} className="relative mb-6">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sc-muted text-sm">+506</span>
              <input
                type="text"
                value={number}
                onChange={(e) => setNumber(e.target.value)}
                placeholder="8XXX-XXXX"
                className="w-full bg-sc-card border border-sc-border rounded-xl pl-14 pr-4 py-3.5 text-sc-text placeholder:text-sc-muted/50 focus:border-sc-accent/50 focus:shadow-glow transition-all font-mono text-lg"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="bg-sc-accent hover:bg-sc-accent-dim disabled:opacity-50 text-sc-bg font-semibold px-5 rounded-xl transition-all active:scale-95"
            >
              {loading ? (
                <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" opacity="0.3" />
                  <path d="M12 2a10 10 0 019.95 9" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-5 h-5">
                  <circle cx="11" cy="11" r="7" />
                  <path d="M21 21l-4.35-4.35" strokeLinecap="round" />
                </svg>
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="bg-sc-danger/10 border border-sc-danger/30 rounded-xl p-4 mb-6">
            <p className="text-sc-danger text-sm font-medium">{error}</p>
          </div>
        )}

        {loading && !result && (
          <div className="space-y-4">
            <div className="shimmer h-40 rounded-xl" />
            <div className="shimmer h-24 rounded-xl" />
            <div className="shimmer h-24 rounded-xl" />
          </div>
        )}

        {result && <ResultView data={result} />}

        {!result && !loading && !error && (
          <div className="text-center py-16">
            <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-sc-card border border-sc-border flex items-center justify-center">
              <svg viewBox="0 0 24 24" fill="none" className="w-10 h-10 text-sc-muted/40">
                <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.362 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.338 1.85.573 2.81.7A2 2 0 0122 16.92z" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <p className="text-sc-muted text-sm mb-1">Ingresa un numero para consultar</p>
            <p className="text-sc-muted/60 text-xs">Formato: 8XXX-XXXX o +506 8XXX-XXXX</p>
          </div>
        )}
      </div>
    </div>
  );
}

function ResultView({ data }) {
  const { scoring, recent_reports } = data;
  const isClean = scoring.total_reports === 0;
  const borderColor =
    scoring.risk_level === "critical"
      ? "border-red-500/40"
      : scoring.risk_level === "high"
      ? "border-orange-500/40"
      : scoring.risk_level === "medium"
      ? "border-yellow-500/40"
      : "border-emerald-500/40";

  const shadowClass =
    scoring.risk_level === "critical" || scoring.risk_level === "high"
      ? "shadow-glow-danger"
      : scoring.risk_level === "medium"
      ? "shadow-glow-warn"
      : "shadow-glow";

  return (
    <div className="space-y-4 animate-in">
      <div className={`bg-sc-card border ${borderColor} ${shadowClass} rounded-2xl p-6`}>
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="font-mono text-xl font-bold text-sc-text">{data.number}</p>
            <p className="text-sc-muted text-xs mt-1">
              Proveedor: {data.carrier} {data.is_blocked && "• BLOQUEADO"}
            </p>
          </div>
          <Badge level={scoring.risk_level} />
        </div>

        <div className={`rounded-xl border px-4 py-3 text-sm ${
          isClean
            ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
            : "bg-sc-surface border-sc-border text-sc-text/80"
        }`}>
          {data.status_message}
        </div>

        <div className="flex justify-center my-6">
          <RiskRing score={scoring.score} level={scoring.risk_level} />
        </div>

        <div className="grid grid-cols-3 gap-3 mt-4">
          <StatBox label="Reportes" value={scoring.total_reports} />
          <StatBox label="Ultimos 7d" value={scoring.recent_reports_7d} />
          <StatBox label="Llamadas 24h" value={scoring.simulated_call_volume} />
        </div>

        <div className="mt-4 pt-4 border-t border-sc-border">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sc-muted text-xs font-semibold uppercase tracking-wider">Categoria</span>
          </div>
          <p className="text-sm font-medium font-mono text-sc-text">{scoring.fraud_category}</p>
        </div>
      </div>

      {scoring.factors.length > 0 && (
        <div className="bg-sc-card border border-sc-border rounded-2xl p-4">
          <h3 className="text-xs font-semibold text-sc-muted uppercase tracking-wider mb-3">
            Factores de riesgo
          </h3>
          <ul className="space-y-2">
            {scoring.factors.map((f, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-sc-text/80">
                <span className="text-sc-warn mt-0.5">
                  <svg viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5">
                    <path d="M8 1l7 14H1L8 1z" />
                  </svg>
                </span>
                {f}
              </li>
            ))}
          </ul>
        </div>
      )}

      {recent_reports.length > 0 && (
        <div className="bg-sc-card border border-sc-border rounded-2xl p-4">
          <h3 className="text-xs font-semibold text-sc-muted uppercase tracking-wider mb-3">
            Reportes recientes ({recent_reports.length})
          </h3>
          <div className="space-y-3">
            {recent_reports.map((r) => (
              <div key={r.id} className="bg-sc-surface rounded-xl p-3 border border-sc-border/50">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-mono text-xs text-sc-accent">{r.category}</span>
                  <Badge level={r.risk_level} />
                </div>
                {r.description && (
                  <p className="text-xs text-sc-muted leading-relaxed">{r.description}</p>
                )}
                <p className="text-[10px] text-sc-muted/60 mt-1.5">
                  {new Date(r.created_at).toLocaleDateString("es-CR", {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function StatBox({ label, value }) {
  return (
    <div className="bg-sc-surface rounded-xl p-3 text-center border border-sc-border/50">
      <p className="text-xl font-bold font-mono text-sc-text">{value}</p>
      <p className="text-[10px] text-sc-muted uppercase tracking-wider mt-0.5">{label}</p>
    </div>
  );
}
