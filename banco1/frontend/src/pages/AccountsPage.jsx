import { useEffect, useState } from "react";
import { apiRequest, formatCurrency, formatDate } from "../api";
import { useAuth } from "../auth";

export default function AccountsPage() {
  const { token } = useAuth();
  const [accounts, setAccounts] = useState([]);
  const [initialBalance, setInitialBalance] = useState(5000);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function loadAccounts() {
    const data = await apiRequest("/accounts/my", { token });
    setAccounts(data);
  }

  useEffect(() => {
    loadAccounts().catch((loadError) => setError(loadError.message));
  }, [token]);

  async function handleCreateAccount(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setSuccess("");

    try {
      await apiRequest("/accounts", {
        method: "POST",
        token,
        body: { initial_balance: Number(initialBalance) },
      });
      setSuccess("Cuenta creada correctamente.");
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
          <p className="eyebrow">Cuentas</p>
          <h2>Mis cuentas bancarias</h2>
        </div>
        <p className="page-copy">Cada cuenta tiene saldo independiente para operar dentro del portal bancario.</p>
      </header>

      <div className="two-column-grid">
        <article className="panel">
          <div className="panel-header">
            <h3>Abrir nueva cuenta</h3>
            <span>Alta rápida</span>
          </div>
          <form className="stack-form" onSubmit={handleCreateAccount}>
            <label>
              Saldo inicial
              <input
                type="number"
                min="0"
                step="0.01"
                value={initialBalance}
                onChange={(event) => setInitialBalance(event.target.value)}
              />
            </label>
            {error ? <p className="form-error">{error}</p> : null}
            {success ? <p className="form-success">{success}</p> : null}
            <button className="primary-button" type="submit" disabled={submitting}>
              {submitting ? "Creando..." : "Crear cuenta"}
            </button>
          </form>
        </article>

        <article className="panel">
          <div className="panel-header">
            <h3>Resumen</h3>
            <span>{accounts.length} cuentas</span>
          </div>
          <div className="summary-grid">
            <div>
              <small>Balance total</small>
              <strong>{formatCurrency(accounts.reduce((sum, account) => sum + account.balance, 0))}</strong>
            </div>
            <div>
              <small>Cuenta mayor</small>
              <strong>
                {formatCurrency(
                  accounts.reduce((max, account) => Math.max(max, account.balance), 0),
                )}
              </strong>
            </div>
          </div>
        </article>
      </div>

      <article className="panel">
        <div className="panel-header">
          <h3>Detalle de cuentas</h3>
          <span>Saldo actualizado</span>
        </div>
        <div className="card-stack">
          {accounts.map((account) => (
            <div className="account-card wide" key={account.id}>
              <div>
                <p>Cuenta {account.account_number}</p>
                <span>ID {account.id} · {formatDate(account.created_at)}</span>
              </div>
              <strong>{formatCurrency(account.balance)}</strong>
            </div>
          ))}
          {!accounts.length ? <p className="empty-state">No hay cuentas creadas todavía.</p> : null}
        </div>
      </article>
    </section>
  );
}
