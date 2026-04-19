const COLORS = {
  critical: { stroke: "#ff3b5c", bg: "rgba(255,59,92,0.08)" },
  high: { stroke: "#ff8c3b", bg: "rgba(255,140,59,0.08)" },
  medium: { stroke: "#ffb020", bg: "rgba(255,176,32,0.08)" },
  low: { stroke: "#00d4aa", bg: "rgba(0,212,170,0.08)" },
};

export default function RiskRing({ score, level, size = 140 }) {
  const cfg = COLORS[level] || COLORS.low;
  const r = (size - 12) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;

  return (
    <div className="risk-ring flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill={cfg.bg}
          stroke="#1a2744"
          strokeWidth={6}
          className="risk-ring-bg"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={cfg.stroke}
          strokeWidth={6}
          strokeLinecap="round"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 1s ease-out" }}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-3xl font-bold font-mono" style={{ color: cfg.stroke }}>
          {score}
        </span>
        <span className="text-[10px] uppercase tracking-widest text-sc-muted font-semibold">
          {level}
        </span>
      </div>
    </div>
  );
}
