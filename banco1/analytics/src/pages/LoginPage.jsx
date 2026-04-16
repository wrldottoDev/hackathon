import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAnalysisAuth } from "../auth";

export default function LoginPage() {
  const { banks, login, selectedBank } = useAnalysisAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    bankId: selectedBank.id,
    email: "demo@example.com",
    password: "demo1234",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      await login(form);
      navigate("/");
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="analysis-auth-shell">
      <div className="analysis-auth-card">
        <p className="analysis-kicker">Cross-Bank Monitoring</p>
        <h1>Consola externa de análisis</h1>
        <p className="analysis-copy">
          Ingresa a un banco específico para revisar alertas, transacciones sospechosas y su red.
        </p>

        <form className="stack-form" onSubmit={handleSubmit}>
          <label>
            Banco
            <select
              value={form.bankId}
              onChange={(event) => setForm({ ...form, bankId: event.target.value })}
            >
              {banks.map((bank) => (
                <option key={bank.id} value={bank.id}>
                  {bank.label}
                </option>
              ))}
            </select>
          </label>

          <label>
            Email
            <input
              type="email"
              value={form.email}
              onChange={(event) => setForm({ ...form, email: event.target.value })}
              required
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
              required
            />
          </label>

          {error ? <p className="form-error">{error}</p> : null}
          <button type="submit" className="primary-button" disabled={submitting}>
            {submitting ? "Ingresando..." : "Entrar a la consola"}
          </button>
        </form>
      </div>
    </div>
  );
}
