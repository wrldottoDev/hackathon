import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

const LEVEL_COLORS = {
  critical: { bg: "bg-red-500/15", text: "text-red-400", border: "border-red-500/30" },
  high: { bg: "bg-orange-500/15", text: "text-orange-400", border: "border-orange-500/30" },
  medium: { bg: "bg-yellow-500/15", text: "text-yellow-400", border: "border-yellow-500/30" },
  low: { bg: "bg-green-500/15", text: "text-green-400", border: "border-green-500/30" },
};

const RULE_ICONS = {
  enlace_sospechoso: "&#128279;",
  analisis_semantico: "&#128269;",
  anomalia_perfil: "&#128100;",
  spam_mensajes_directos: "&#9888;",
};

export default function AnalyticsDashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .fullScan()
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="max-w-lg mx-auto flex justify-center py-20">
        <div className="text-center">
          <div className="w-10 h-10 border-2 border-finsta-accent border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-finsta-muted text-sm mt-4">Escaneando red social...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="max-w-lg mx-auto text-center py-20 text-finsta-muted">
        Error al conectar con el motor de analisis
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto pb-20">
      {/* Header */}
      <header className="sticky top-0 bg-finsta-bg/95 backdrop-blur border-b border-finsta-border z-40 px-4 py-3 flex items-center gap-3">
        <button onClick={() => navigate("/")} className="text-finsta-text">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-6 h-6">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
        </button>
        <h2 className="font-bold text-lg flex-1">
          <span className="gradient-text">FlowLens</span>
          <span className="text-finsta-muted text-xs ml-2">Analytics</span>
        </h2>
      </header>

      {/* Summary cards */}
      <div className="px-4 py-4 grid grid-cols-2 gap-3">
        <div className="bg-finsta-card rounded-xl p-4 border border-finsta-border">
          <div className="text-finsta-muted text-xs mb-1">Posts analizados</div>
          <div className="text-2xl font-bold">{data.total_analyzed_posts}</div>
          <div className="text-red-400 text-xs mt-1">
            {data.total_dangerous_posts} peligrosos
          </div>
        </div>
        <div className="bg-finsta-card rounded-xl p-4 border border-finsta-border">
          <div className="text-finsta-muted text-xs mb-1">DMs analizados</div>
          <div className="text-2xl font-bold">{data.total_analyzed_messages}</div>
          <div className="text-red-400 text-xs mt-1">
            {data.total_dangerous_messages} peligrosos
          </div>
        </div>
      </div>

      {/* Dangerous users */}
      {data.dangerous_users.length > 0 && (
        <div className="px-4 pb-3">
          <h3 className="text-sm font-semibold text-finsta-muted mb-2">
            Usuarios sospechosos detectados
          </h3>
          <div className="flex flex-wrap gap-2">
            {data.dangerous_users.map((username) => (
              <span
                key={username}
                className="bg-red-500/15 text-red-400 border border-red-500/30 px-3 py-1 rounded-full text-xs font-semibold"
              >
                @{username}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Alert list */}
      <div className="px-4">
        <h3 className="text-sm font-semibold text-finsta-muted mb-3">
          Alertas de captacion detectadas
        </h3>
        <div className="space-y-3">
          {data.top_alerts.map((alert, index) => {
            const colors = LEVEL_COLORS[alert.risk_level] || LEVEL_COLORS.medium;
            return (
              <div
                key={index}
                className={`${colors.bg} border ${colors.border} rounded-xl p-4`}
              >
                {/* Alert header */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${colors.bg} ${colors.text}`}
                    >
                      {alert.risk_level}
                    </span>
                    <span className="text-xs text-finsta-muted">
                      {alert.target_type === "post" ? "Publicacion" : "Mensaje"} #{alert.target_id}
                    </span>
                  </div>
                  <div className={`text-lg font-bold ${colors.text}`}>
                    {alert.total_score}
                    <span className="text-[10px] text-finsta-muted">/100</span>
                  </div>
                </div>

                {/* User */}
                <div className="text-sm font-semibold mb-2">
                  @{alert.username}
                </div>

                {/* Rules triggered */}
                <div className="space-y-1.5">
                  {alert.rules_triggered.map((rule, ri) => (
                    <div key={ri} className="flex items-start gap-2 text-xs">
                      <span
                        className={`${colors.text} flex-shrink-0 mt-0.5`}
                        dangerouslySetInnerHTML={{
                          __html: RULE_ICONS[rule.rule_name] || "&#9679;",
                        }}
                      />
                      <div>
                        <span className={`font-semibold ${colors.text}`}>
                          {rule.rule_name.replace(/_/g, " ")}
                        </span>
                        <span className="text-finsta-muted ml-1">(+{rule.score})</span>
                        <p className="text-finsta-muted mt-0.5 leading-snug">
                          {rule.detail.length > 120
                            ? rule.detail.slice(0, 117) + "..."
                            : rule.detail}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
