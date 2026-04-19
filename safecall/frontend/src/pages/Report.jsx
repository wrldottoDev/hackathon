import { useState, useEffect } from "react";
import { api } from "../api";
import Header from "../components/Header";

const CATEGORIES = [
  { value: "trata_personas", label: "Trata de Personas", severity: "critical" },
  { value: "secuestro_virtual", label: "Secuestro Virtual", severity: "critical" },
  { value: "extorsion", label: "Extorsion", severity: "critical" },
  { value: "sim_swapping", label: "SIM Swapping", severity: "critical" },
  { value: "estafa", label: "Estafa", severity: "medium" },
  { value: "phishing", label: "Phishing", severity: "medium" },
  { value: "vishing", label: "Vishing", severity: "medium" },
  { value: "suplantacion", label: "Suplantacion", severity: "medium" },
];

export default function Report() {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({
    reporter_id: "",
    reported_number: "",
    category: "",
    description: "",
    evidence_hash: "",
    consent_data_processing: false,
  });
  const [sending, setSending] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.listUsers().then(setUsers).catch(() => {});
  }, []);

  const update = (field, value) => setForm((f) => ({ ...f, [field]: value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.reporter_id || !form.reported_number || !form.category) {
      setError("Completa los campos requeridos");
      return;
    }
    if (!form.consent_data_processing) {
      setError("Debes aceptar el consentimiento de procesamiento de datos (Ley 8968)");
      return;
    }
    setSending(true);
    setError("");
    setSuccess(null);
    try {
      const payload = {
        ...form,
        reporter_id: parseInt(form.reporter_id),
        reported_number: form.reported_number.startsWith("+506")
          ? form.reported_number
          : `+506${form.reported_number}`,
        evidence_hash: form.evidence_hash || null,
      };
      const data = await api.createReport(payload);
      setSuccess(data);
      setForm({
        reporter_id: form.reporter_id,
        reported_number: "",
        category: "",
        description: "",
        evidence_hash: "",
        consent_data_processing: false,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setSending(false);
    }
  };

  const selectedCat = CATEGORIES.find((c) => c.value === form.category);

  return (
    <div className="max-w-lg mx-auto">
      <Header title="Reportar Numero" subtitle="Reporte anonimo y seguro" />

      <form onSubmit={handleSubmit} className="px-4 space-y-4">
        <div>
          <label className="block text-xs font-semibold text-sc-muted uppercase tracking-wider mb-1.5">
            Reportante *
          </label>
          <select
            value={form.reporter_id}
            onChange={(e) => update("reporter_id", e.target.value)}
            className="w-full bg-sc-card border border-sc-border rounded-xl px-4 py-3 text-sc-text focus:border-sc-accent/50 transition-colors appearance-none"
          >
            <option value="">Seleccionar usuario</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.full_name} ({u.assigned_simulated_number})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-sc-muted uppercase tracking-wider mb-1.5">
            Numero a reportar *
          </label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sc-muted text-sm">+506</span>
            <input
              type="text"
              value={form.reported_number}
              onChange={(e) => update("reported_number", e.target.value)}
              placeholder="8XXX-XXXX"
              className="w-full bg-sc-card border border-sc-border rounded-xl pl-14 pr-4 py-3 text-sc-text placeholder:text-sc-muted/50 focus:border-sc-accent/50 transition-colors font-mono"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-sc-muted uppercase tracking-wider mb-1.5">
            Categoria *
          </label>
          <div className="grid grid-cols-2 gap-2">
            {CATEGORIES.map((cat) => (
              <button
                key={cat.value}
                type="button"
                onClick={() => update("category", cat.value)}
                className={`text-left px-3 py-2.5 rounded-xl border text-sm font-medium transition-all ${
                  form.category === cat.value
                    ? cat.severity === "critical"
                      ? "bg-red-500/15 border-red-500/40 text-red-400"
                      : "bg-yellow-500/15 border-yellow-500/40 text-yellow-400"
                    : "bg-sc-card border-sc-border text-sc-muted hover:border-sc-border hover:text-sc-text"
                }`}
              >
                <span className="block text-xs">{cat.label}</span>
                {cat.severity === "critical" && (
                  <span className="text-[9px] uppercase tracking-wider opacity-60">Alto riesgo</span>
                )}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-sc-muted uppercase tracking-wider mb-1.5">
            Descripcion
          </label>
          <textarea
            value={form.description}
            onChange={(e) => update("description", e.target.value)}
            rows={3}
            placeholder="Describe la situacion..."
            className="w-full bg-sc-card border border-sc-border rounded-xl px-4 py-3 text-sc-text placeholder:text-sc-muted/50 focus:border-sc-accent/50 transition-colors resize-none"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-sc-muted uppercase tracking-wider mb-1.5">
            Hash de evidencia
          </label>
          <input
            type="text"
            value={form.evidence_hash}
            onChange={(e) => update("evidence_hash", e.target.value)}
            placeholder="SHA-256 del archivo de evidencia (opcional)"
            className="w-full bg-sc-card border border-sc-border rounded-xl px-4 py-3 text-sc-text placeholder:text-sc-muted/50 focus:border-sc-accent/50 transition-colors font-mono text-xs"
          />
        </div>

        <div className="bg-sc-surface border border-sc-border rounded-xl p-4">
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={form.consent_data_processing}
              onChange={(e) => update("consent_data_processing", e.target.checked)}
              className="mt-1 accent-sc-accent w-4 h-4 rounded"
            />
            <span className="text-xs text-sc-muted leading-relaxed">
              Autorizo el procesamiento de mis datos conforme a la{" "}
              <span className="text-sc-accent font-medium">Ley 8968</span> de Proteccion de la Persona
              frente al Tratamiento de sus Datos Personales. Mi IP sera anonimizada mediante hash.
            </span>
          </label>
        </div>

        {error && (
          <div className="bg-sc-danger/10 border border-sc-danger/30 rounded-xl p-3">
            <p className="text-sc-danger text-sm">{error}</p>
          </div>
        )}

        {success && (
          <div className="bg-sc-accent/10 border border-sc-accent/30 rounded-xl p-4">
            <p className="text-sc-accent text-sm font-semibold mb-1">Reporte registrado</p>
            <p className="text-sc-muted text-xs">
              ID: {success.id} • Nivel: {success.risk_level}
              {success.forwarded_to_analytics && " • Enviado a Analytics"}
            </p>
          </div>
        )}

        <button
          type="submit"
          disabled={sending}
          className="w-full bg-sc-danger hover:bg-sc-danger-dim disabled:opacity-50 text-white font-semibold py-3.5 rounded-xl transition-all active:scale-[0.98] flex items-center justify-center gap-2"
        >
          {sending ? (
            <>
              <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" opacity="0.3" />
                <path d="M12 2a10 10 0 019.95 9" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
              </svg>
              Enviando...
            </>
          ) : (
            <>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="w-4 h-4">
                <path d="M12 9v4m0 4h.01" strokeLinecap="round" />
                <circle cx="12" cy="12" r="10" />
              </svg>
              Enviar Reporte
            </>
          )}
        </button>

        {selectedCat?.severity === "critical" && (
          <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-3 text-center">
            <p className="text-red-400 text-xs">
              Los reportes de <span className="font-semibold">{selectedCat.label}</span> son enviados
              automaticamente al servicio de analytics para seguimiento inmediato.
            </p>
          </div>
        )}
      </form>
    </div>
  );
}
