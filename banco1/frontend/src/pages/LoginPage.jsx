import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import { BANK_NAME, DEMO_EMAIL } from "../config";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: DEMO_EMAIL,
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
    <div className="auth-shell">
      <div className="auth-card">
        <p className="eyebrow">{BANK_NAME}</p>
        <h1>Ingreso seguro para la demo</h1>
        <p className="auth-copy">
          Entra con la cuenta demo o con un usuario nuevo para administrar tus cuentas y transferencias en {BANK_NAME}.
        </p>

        <form className="stack-form" onSubmit={handleSubmit}>
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
          <button className="primary-button" type="submit" disabled={submitting}>
            {submitting ? "Ingresando..." : "Iniciar sesión"}
          </button>
        </form>

        <p className="auth-footer">
          ¿No tienes usuario? <Link to="/register">Crear cuenta</Link>
        </p>
      </div>
    </div>
  );
}
