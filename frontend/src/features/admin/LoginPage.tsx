import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "@/features/admin/adminApi";
import { setAccessToken } from "@/shared/auth/token";

export function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [slug, setSlug] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await login(email, password, slug.trim() || undefined);
      setAccessToken(res.access_token);
      navigate("/admin", { replace: true });
    } catch {
      setError("Credenciales inválidas o tenant incorrecto.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 360, margin: "48px auto", padding: 16 }}>
      <h1>Ingresar</h1>
      <form onSubmit={onSubmit}>
        {error && <p style={{ color: "#8b0000" }} role="alert">{error}</p>}
        <label style={{ display: "block", marginBottom: 8 }}>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: "100%", padding: 8 }}
          />
        </label>
        <label style={{ display: "block", marginBottom: 8 }}>
          Contraseña
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: "100%", padding: 8 }}
          />
        </label>
        <label style={{ display: "block", marginBottom: 12 }}>
          Slug del negocio (si tenés más de uno)
          <input
            type="text"
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            style={{ width: "100%", padding: 8 }}
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Entrando…" : "Entrar"}
        </button>
      </form>
    </div>
  );
}
