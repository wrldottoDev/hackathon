const STYLES = {
  critical: "bg-red-500/15 text-red-400 border-red-500/30",
  high: "bg-orange-500/15 text-orange-400 border-orange-500/30",
  medium: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
  low: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  pending: "bg-slate-500/15 text-slate-400 border-slate-500/30",
};

export default function Badge({ level, className = "" }) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider border ${
        STYLES[level] || STYLES.pending
      } ${className}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5 pulse-dot" />
      {level}
    </span>
  );
}
