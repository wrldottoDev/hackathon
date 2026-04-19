export default function Header({ title, subtitle }) {
  return (
    <header className="px-4 pt-6 pb-4">
      <div className="flex items-center gap-3 mb-1">
        <div className="w-8 h-8 rounded-lg bg-sc-accent/10 flex items-center justify-center">
          <svg viewBox="0 0 24 24" fill="none" className="w-5 h-5 text-sc-accent">
            <path
              d="M12 2L3 7v5c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5z"
              stroke="currentColor"
              strokeWidth={1.8}
              strokeLinejoin="round"
            />
            <path d="M9 12l2 2 4-4" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <div>
          <h1 className="text-lg font-bold text-sc-text">{title}</h1>
          {subtitle && <p className="text-xs text-sc-muted">{subtitle}</p>}
        </div>
      </div>
    </header>
  );
}
