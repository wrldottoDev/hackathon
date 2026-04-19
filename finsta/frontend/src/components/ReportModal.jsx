import { useState } from "react";
import { api } from "../api";

const REASONS = [
  { value: "sospecha_captacion", label: "Sospecha de captación / trata" },
  { value: "fraude", label: "Fraude o estafa" },
  { value: "spam", label: "Spam o contenido no deseado" },
  { value: "acoso", label: "Acoso o intimidación" },
  { value: "otro", label: "Otro" },
];

export default function ReportModal({ onClose, postId, messageId, reportedUserId, currentUserId }) {
  const [reason, setReason] = useState("");
  const [description, setDescription] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!reason) return;
    setLoading(true);
    try {
      await api.createReport(currentUserId, {
        reported_user_id: reportedUserId,
        post_id: postId || null,
        message_id: messageId || null,
        reason,
        description,
      });
      setSent(true);
      setTimeout(onClose, 1500);
    } catch {
      alert("Error al enviar el reporte.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-end sm:items-center justify-center" onClick={onClose}>
      <div
        className="bg-finsta-card rounded-t-2xl sm:rounded-2xl w-full max-w-md p-5 space-y-4"
        onClick={(e) => e.stopPropagation()}
      >
        {sent ? (
          <div className="text-center py-6">
            <div className="text-3xl mb-2">&#10003;</div>
            <p className="font-semibold">Reporte enviado</p>
            <p className="text-finsta-muted text-sm">Gracias por ayudar a mantener segura la comunidad.</p>
          </div>
        ) : (
          <>
            <h3 className="font-bold text-lg text-center">Reportar</h3>
            <p className="text-finsta-muted text-sm text-center">
              Selecciona el motivo del reporte
            </p>
            <div className="space-y-2">
              {REASONS.map((r) => (
                <button
                  key={r.value}
                  onClick={() => setReason(r.value)}
                  className={`w-full text-left px-4 py-3 rounded-xl text-sm transition-colors ${
                    reason === r.value
                      ? "bg-finsta-accent/20 text-finsta-accent border border-finsta-accent/40"
                      : "bg-finsta-bg hover:bg-finsta-border"
                  }`}
                >
                  {r.label}
                </button>
              ))}
            </div>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe lo que observas (opcional)..."
              className="w-full bg-finsta-bg border border-finsta-border rounded-xl px-3 py-2 text-sm resize-none h-20 focus:outline-none focus:border-finsta-accent/50"
            />
            <div className="flex gap-3">
              <button
                onClick={onClose}
                className="flex-1 py-2.5 rounded-xl bg-finsta-border text-sm font-semibold"
              >
                Cancelar
              </button>
              <button
                onClick={handleSubmit}
                disabled={!reason || loading}
                className="flex-1 py-2.5 rounded-xl bg-finsta-accent text-white text-sm font-semibold disabled:opacity-40"
              >
                {loading ? "Enviando..." : "Enviar reporte"}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
