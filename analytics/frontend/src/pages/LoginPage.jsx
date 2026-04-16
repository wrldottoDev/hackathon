import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAnalysisAuth } from "../auth";
import { DEFAULT_ANALYTICS_KEY } from "../config";

export default function LoginPage() {
  const { login } = useAnalysisAuth();
  const navigate = useNavigate();
  const [apiKey, setApiKey] = useState(DEFAULT_ANALYTICS_KEY);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      await login(apiKey);
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
        <p className="analysis-kicker">FlowLens Console</p>
        <h1>Entrar al panel analítico</h1>
        <p className="analysis-copy">
          Usa la API key del panel para revisar Banco A, Banco B y el consolidado desde una sola consola.
        </p>

        <form className="stack-form" onSubmit={handleSubmit}>
          <label>
            API key
            <input
              type="password"
              value={apiKey}
              onChange={(event) => setApiKey(event.target.value)}
              required
            />
          </label>

          {error ? <p className="form-error">{error}</p> : null}
          <button type="submit" className="primary-button" disabled={submitting}>
            {submitting ? "Validando..." : "Entrar al panel"}
          </button>
        </form>
      </div>
    </div>
  );
}
