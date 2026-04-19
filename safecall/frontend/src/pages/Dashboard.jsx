import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import Header from "../components/Header";
import Badge from "../components/Badge";

export default function Dashboard() {
  const [reports, setReports] = useState([]);
  const [phoneNumbers, setPhoneNumbers] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      api.listReports(0, 100),
      api.listPhoneNumbers(0, 100),
    ])
      .then(([reportRows, phoneRows]) => {
        setReports(reportRows);
        setPhoneNumbers(phoneRows);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const stats = {
    total: reports.length,
    critical: reports.filter((r) => r.risk_level === "critical").length,
    high: reports.filter((r) => r.risk_level === "high").length,
    forwarded: reports.filter((r) => r.forwarded_to_analytics).length,
  };

  const categoryCounts = {};
  reports.forEach((r) => {
    categoryCounts[r.category] = (categoryCounts[r.category] || 0) + 1;
  });
  const sortedCategories = Object.entries(categoryCounts).sort((a, b) => b[1] - a[1]);

  return (
    <div className="max-w-lg mx-auto">
      <Header title="Monitor" subtitle="Panel de inteligencia SafeCall" />

      <div className="px-4 space-y-4">
        {loading ? (
          <div className="space-y-4">
            <div className="shimmer h-28 rounded-xl" />
            <div className="shimmer h-40 rounded-xl" />
          </div>
        ) : (
          <>
            <div className="grid grid-cols-4 gap-2">
              <MetricCard value={stats.total} label="Reportes" color="text-sc-accent" />
              <MetricCard value={stats.critical} label="Criticos" color="text-red-400" />
              <MetricCard value={stats.high} label="Altos" color="text-orange-400" />
              <MetricCard value={stats.forwarded} label="Enviados" color="text-sc-blue" />
            </div>

            <div className="bg-sc-card border border-sc-border rounded-2xl p-4">
              <h3 className="text-xs font-semibold text-sc-muted uppercase tracking-wider mb-3">
                Numeros monitoreados ({phoneNumbers.length})
              </h3>
              <div className="space-y-2">
                {phoneNumbers.map((phone) => {
                  return (
                    <button
                      key={phone.number}
                      onClick={() => navigate(`/?q=${phone.number}`)}
                      className="w-full flex items-center justify-between bg-sc-surface hover:bg-sc-card-hover border border-sc-border/50 rounded-xl p-3 transition-colors text-left"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg bg-sc-border/50 flex items-center justify-center">
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} className="w-4 h-4 text-sc-muted">
                            <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6A19.79 19.79 0 012.12 4.18 2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.362 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.338 1.85.573 2.81.7A2 2 0 0122 16.92z" />
                          </svg>
                        </div>
                        <div>
                          <p className="font-mono text-sm font-medium text-sc-text">{phone.number}</p>
                          <p className="text-[10px] text-sc-muted">
                            {phone.carrier} • {phone.status_message}
                          </p>
                        </div>
                      </div>
                      <Badge level={phone.risk_level} />
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="bg-sc-card border border-sc-border rounded-2xl p-4">
              <h3 className="text-xs font-semibold text-sc-muted uppercase tracking-wider mb-3">
                Categorias
              </h3>
              <div className="space-y-2">
                {sortedCategories.map(([cat, count]) => {
                  const pct = Math.round((count / stats.total) * 100);
                  const isHigh = [
                    "trata_personas",
                    "sim_swapping",
                    "extorsion",
                    "secuestro_virtual",
                  ].includes(cat);
                  return (
                    <div key={cat}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium text-sc-text">{cat}</span>
                        <span className="text-xs font-mono text-sc-muted">
                          {count} ({pct}%)
                        </span>
                      </div>
                      <div className="h-1.5 bg-sc-border rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${
                            isHigh ? "bg-red-500" : "bg-yellow-500"
                          }`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="bg-sc-card border border-sc-border rounded-2xl p-4">
              <h3 className="text-xs font-semibold text-sc-muted uppercase tracking-wider mb-3">
                Actividad reciente
              </h3>
              <div className="space-y-2">
                {reports.slice(0, 10).map((r) => (
                  <div
                    key={r.id}
                    className="flex items-center gap-3 bg-sc-surface border border-sc-border/50 rounded-xl p-3"
                  >
                    <div
                      className={`w-2 h-2 rounded-full flex-shrink-0 ${
                        r.risk_level === "critical"
                          ? "bg-red-500"
                          : r.risk_level === "high"
                          ? "bg-orange-500"
                          : r.risk_level === "medium"
                          ? "bg-yellow-500"
                          : "bg-emerald-500"
                      }`}
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="font-mono text-xs text-sc-text truncate">{r.reported_number}</p>
                        <span className="text-[10px] text-sc-muted font-mono ml-2 flex-shrink-0">
                          {r.category}
                        </span>
                      </div>
                      {r.description && (
                        <p className="text-[10px] text-sc-muted truncate mt-0.5">{r.description}</p>
                      )}
                    </div>
                    {r.forwarded_to_analytics && (
                      <svg viewBox="0 0 16 16" fill="currentColor" className="w-3 h-3 text-sc-blue flex-shrink-0">
                        <path d="M8 0a8 8 0 100 16A8 8 0 008 0zm3.5 7.5l-4 4a.5.5 0 01-.7 0l-2-2a.5.5 0 01.7-.7L7.1 10.4l3.6-3.6a.5.5 0 01.8.7z" />
                      </svg>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function MetricCard({ value, label, color }) {
  return (
    <div className="bg-sc-card border border-sc-border rounded-xl p-3 text-center">
      <p className={`text-2xl font-bold font-mono ${color}`}>{value}</p>
      <p className="text-[9px] text-sc-muted uppercase tracking-wider mt-0.5">{label}</p>
    </div>
  );
}
