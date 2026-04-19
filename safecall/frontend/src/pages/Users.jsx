import { useState, useEffect } from "react";
import { api } from "../api";
import Header from "../components/Header";

export default function Users() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ full_name: "", email: "" });
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const load = () => {
    api.listUsers().then(setUsers).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!form.full_name.trim() || !form.email.trim()) {
      setError("Nombre y email son requeridos");
      return;
    }
    setSending(true);
    setError("");
    try {
      await api.registerUser(form);
      setForm({ full_name: "", email: "" });
      setShowForm(false);
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto">
      <Header title="Usuarios" subtitle="Registro y gestion" />

      <div className="px-4 space-y-4">
        <button
          onClick={() => setShowForm(!showForm)}
          className="w-full flex items-center justify-center gap-2 bg-sc-accent/10 hover:bg-sc-accent/20 border border-sc-accent/30 text-sc-accent font-semibold py-3 rounded-xl transition-all"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-4 h-4">
            {showForm ? <path d="M18 6L6 18M6 6l12 12" /> : <path d="M12 5v14M5 12h14" />}
          </svg>
          {showForm ? "Cancelar" : "Registrar Usuario"}
        </button>

        {showForm && (
          <form
            onSubmit={handleRegister}
            className="bg-sc-card border border-sc-accent/30 rounded-2xl p-4 space-y-3 shadow-glow"
          >
            <div>
              <label className="block text-xs font-semibold text-sc-muted uppercase tracking-wider mb-1">
                Nombre completo
              </label>
              <input
                type="text"
                value={form.full_name}
                onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))}
                placeholder="Maria Lopez Jimenez"
                className="w-full bg-sc-surface border border-sc-border rounded-xl px-4 py-2.5 text-sc-text placeholder:text-sc-muted/50 focus:border-sc-accent/50 transition-colors"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-sc-muted uppercase tracking-wider mb-1">
                Email
              </label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                placeholder="maria@ejemplo.cr"
                className="w-full bg-sc-surface border border-sc-border rounded-xl px-4 py-2.5 text-sc-text placeholder:text-sc-muted/50 focus:border-sc-accent/50 transition-colors"
              />
            </div>
            {error && <p className="text-sc-danger text-xs">{error}</p>}
            <button
              type="submit"
              disabled={sending}
              className="w-full bg-sc-accent hover:bg-sc-accent-dim disabled:opacity-50 text-sc-bg font-semibold py-2.5 rounded-xl transition-all"
            >
              {sending ? "Registrando..." : "Registrar"}
            </button>
            <p className="text-[10px] text-sc-muted text-center">
              Se asignara automaticamente un numero +506 8XXX-XXXX simulado
            </p>
          </form>
        )}

        {loading ? (
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="shimmer h-20 rounded-xl" />
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {users.map((u) => (
              <div
                key={u.id}
                className="bg-sc-card border border-sc-border rounded-xl p-4 flex items-center gap-3"
              >
                <div className="w-10 h-10 rounded-full bg-sc-accent/10 flex items-center justify-center flex-shrink-0">
                  <span className="text-sc-accent font-bold text-sm">
                    {u.full_name
                      .split(" ")
                      .map((w) => w[0])
                      .slice(0, 2)
                      .join("")}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-sc-text truncate">{u.full_name}</p>
                  <p className="text-xs text-sc-muted truncate">{u.email}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="font-mono text-[11px] text-sc-accent">
                      {u.assigned_simulated_number}
                    </span>
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
                        u.is_active ? "bg-emerald-500" : "bg-sc-muted"
                      }`}
                    />
                  </div>
                </div>
                <div className="text-[10px] text-sc-muted text-right flex-shrink-0">
                  ID: {u.id}
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && users.length === 0 && (
          <div className="text-center py-12">
            <p className="text-sc-muted text-sm">No hay usuarios registrados</p>
          </div>
        )}
      </div>
    </div>
  );
}
