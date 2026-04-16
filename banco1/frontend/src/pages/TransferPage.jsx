import { useEffect, useState } from "react";
import { apiRequest, formatCurrency } from "../api";
import { useAuth } from "../auth";

export default function TransferPage() {
  const { token } = useAuth();
  const [myAccounts, setMyAccounts] = useState([]);
  const [allAccounts, setAllAccounts] = useState([]);
  const [form, setForm] = useState({
    source_account_id: "",
    destination_account_id: "",
    amount: 500,
    channel: "web",
    location: "San Jose, CR",
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function loadAccounts() {
    const [mine, all] = await Promise.all([
      apiRequest("/accounts/my", { token }),
      apiRequest("/accounts", { token }),
    ]);
    setMyAccounts(mine);
    setAllAccounts(all);
    if (mine.length && !form.source_account_id) {
      setForm((current) => ({ ...current, source_account_id: String(mine[0].id) }));
    }
  }

  useEffect(() => {
    loadAccounts().catch((loadError) => setError(loadError.message));
  }, [token]);

  const destinationOptions = allAccounts.filter(
    (account) => String(account.id) !== String(form.source_account_id),
  );

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setMessage("");

    try {
      await apiRequest("/transactions", {
        method: "POST",
        token,
        body: {
          ...form,
          source_account_id: Number(form.source_account_id),
          destination_account_id: Number(form.destination_account_id),
          amount: Number(form.amount),
        },
      });
      setMessage("Transferencia completada y analizada por el motor de riesgo.");
      await loadAccounts();
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Transferencias</p>
          <h2>Mueve dinero entre cuentas</h2>
        </div>
        <p className="page-copy">
          Cada transferencia actualiza saldos en tiempo real y dispara evaluación de riesgo.
        </p>
      </header>

      <div className="two-column-grid">
        <article className="panel">
          <div className="panel-header">
            <h3>Nueva transferencia</h3>
            <span>Validaciones activas</span>
          </div>

          <form className="stack-form" onSubmit={handleSubmit}>
            <label>
              Cuenta origen
              <select
                value={form.source_account_id}
                onChange={(event) =>
                  setForm({ ...form, source_account_id: event.target.value, destination_account_id: "" })
                }
                required
              >
                <option value="">Selecciona una cuenta</option>
                {myAccounts.map((account) => (
                  <option key={account.id} value={account.id}>
                    {account.account_number} · {formatCurrency(account.balance)}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Cuenta destino
              <select
                value={form.destination_account_id}
                onChange={(event) => setForm({ ...form, destination_account_id: event.target.value })}
                required
              >
                <option value="">Selecciona destino</option>
                {destinationOptions.map((account) => (
                  <option key={account.id} value={account.id}>
                    #{account.id} · {account.account_number}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Monto
              <input
                type="number"
                min="0.01"
                step="0.01"
                value={form.amount}
                onChange={(event) => setForm({ ...form, amount: event.target.value })}
                required
              />
            </label>

            <div className="inline-fields">
              <label>
                Canal
                <select
                  value={form.channel}
                  onChange={(event) => setForm({ ...form, channel: event.target.value })}
                >
                  <option value="web">web</option>
                  <option value="mobile">mobile</option>
                  <option value="atm">atm</option>
                  <option value="api">api</option>
                </select>
              </label>

              <label>
                Ubicación
                <input
                  type="text"
                  value={form.location}
                  onChange={(event) => setForm({ ...form, location: event.target.value })}
                  required
                />
              </label>
            </div>

            {error ? <p className="form-error">{error}</p> : null}
            {message ? <p className="form-success">{message}</p> : null}
            <button className="primary-button" type="submit" disabled={submitting || !myAccounts.length}>
              {submitting ? "Procesando..." : "Enviar transferencia"}
            </button>
          </form>
        </article>

        <article className="panel">
          <div className="panel-header">
            <h3>Cuentas origen</h3>
            <span>Disponibles</span>
          </div>
          <div className="card-stack">
            {myAccounts.map((account) => (
              <div className="account-card" key={account.id}>
                <div>
                  <p>{account.account_number}</p>
                  <span>ID {account.id}</span>
                </div>
                <strong>{formatCurrency(account.balance)}</strong>
              </div>
            ))}
            {!myAccounts.length ? (
              <p className="empty-state">Necesitas al menos una cuenta para transferir.</p>
            ) : null}
          </div>
        </article>
      </div>
    </section>
  );
}
