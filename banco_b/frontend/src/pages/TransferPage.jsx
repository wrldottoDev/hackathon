import { useEffect, useState } from "react";
import { apiRequest, formatCurrency } from "../api";
import { useAuth } from "../auth";
import { BANK_CODE, BANK_NAME } from "../config";

const CHANNELS = [
  { value: "web", label: "Web" },
  { value: "mobile", label: "Móvil" },
  { value: "atm", label: "ATM" },
  { value: "api", label: "API" },
];

export default function TransferPage() {
  const { token } = useAuth();
  const [accounts, setAccounts] = useState([]);
  const [form, setForm] = useState({
    source_account_number: "",
    destination_account_number: "",
    amount: "",
    channel: "web",
    location: "",
    description: "",
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    apiRequest("/accounts/my", {}, token).then((accs) => {
      setAccounts(accs);
      if (accs.length > 0) {
        setForm((f) => ({ ...f, source_account_number: accs[0].account_number }));
      }
    });
  }, [token]);

  const handleChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setSuccess("");
    setLoading(true);
    try {
      const destinationBankCode =
        form.destination_account_number.split("-")[0]?.trim().toUpperCase() || "";
      const isInterbank = destinationBankCode && destinationBankCode !== BANK_CODE;
      await apiRequest(isInterbank ? "/transactions/interbank" : "/transactions/internal", {
        method: "POST",
        body: JSON.stringify({ ...form, amount: parseFloat(form.amount) }),
      }, token);
      setSuccess(
        isInterbank
          ? "Transferencia interbancaria realizada correctamente"
          : "Transferencia interna realizada correctamente",
      );
      setForm((f) => ({
        ...f,
        destination_account_number: "",
        amount: "",
        location: "",
        description: "",
      }));
      // Refresh accounts to show updated balance
      apiRequest("/accounts/my", {}, token).then(setAccounts);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const sourceAccount = accounts.find((a) => a.account_number === form.source_account_number);

  return (
    <>
      <h1 className="page-title">Transferir fondos</h1>
      <p className="page-subtitle">
        Transfiere dinero dentro de {BANK_NAME} o hacia otro banco conectado a FlowLens
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 320px", gap: 20 }}>
        {/* Formulario */}
        <div className="card">
          {error   && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Cuenta origen</label>
              <select
                name="source_account_number"
                value={form.source_account_number}
                onChange={handleChange}
                required
              >
                {accounts.map((a) => (
                  <option key={a.id} value={a.account_number}>
                    {a.account_number} — {formatCurrency(a.balance, a.currency)}
                  </option>
                ))}
              </select>
              {sourceAccount && (
                <span className="form-hint">
                  Saldo disponible: {formatCurrency(sourceAccount.balance, sourceAccount.currency)}
                </span>
              )}
            </div>

            <div className="form-group">
              <label>Cuenta destino</label>
              <input
                name="destination_account_number"
                type="text"
                placeholder={`${BANK_CODE}-XXXXXXXXXX o cuenta de otro banco FlowLens`}
                value={form.destination_account_number}
                onChange={handleChange}
                required
              />
              <span className="form-hint">
                Usa el número completo. Si el prefijo no es {BANK_CODE}, se enviará como transferencia interbancaria.
              </span>
            </div>

            <div className="form-group">
              <label>Monto (CRC)</label>
              <input
                name="amount"
                type="number"
                min="0.01"
                step="0.01"
                placeholder="0.00"
                value={form.amount}
                onChange={handleChange}
                required
              />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div className="form-group">
                <label>Canal</label>
                <select name="channel" value={form.channel} onChange={handleChange}>
                  {CHANNELS.map((c) => (
                    <option key={c.value} value={c.value}>{c.label}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Ubicación (opcional)</label>
                <input
                  name="location"
                  type="text"
                  placeholder="San José, CR"
                  value={form.location}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Descripción (opcional)</label>
              <input
                name="description"
                type="text"
                placeholder="Ej: Pago de alquiler"
                value={form.description}
                onChange={handleChange}
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-full"
              disabled={loading || accounts.length === 0}
            >
              {loading ? "Procesando…" : "Realizar transferencia"}
            </button>
          </form>
        </div>

        {/* Panel de cuentas */}
        <div>
          <h2 style={{ fontSize: 14, fontWeight: 600, color: "var(--muted)", marginBottom: 12 }}>
            TUS CUENTAS
          </h2>
          {accounts.length === 0 ? (
            <div className="card">
              <p style={{ color: "var(--muted)", fontSize: 13 }}>
                No tienes cuentas activas.
              </p>
            </div>
          ) : (
            accounts.map((a) => (
              <div
                key={a.id}
                className="account-card"
                style={{
                  opacity: a.account_number === form.source_account_number ? 1 : 0.6,
                  cursor: "pointer",
                }}
                onClick={() =>
                  setForm((f) => ({ ...f, source_account_number: a.account_number }))
                }
              >
                <div className="acc-number">{a.account_number}</div>
                <div className="acc-balance">{formatCurrency(a.balance, a.currency)}</div>
                <div className="acc-currency">{a.currency} · {a.status}</div>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
}
