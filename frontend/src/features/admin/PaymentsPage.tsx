import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { adminFetch } from "@/shared/api/adminClient";
import { getAccessToken } from "@/shared/auth/token";

type MpStatus = { connected: boolean; mp_user_id: string | null };

export function PaymentsPage() {
  const token = getAccessToken();
  const [status, setStatus] = useState<MpStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    adminFetch<MpStatus>("/admin/payments/status")
      .then(setStatus)
      .catch(() => setError("Requiere plan Pro o superior con pagos online."));
  }, [token]);

  if (!token) return <Navigate to="/admin/login" replace />;

  const connect = async () => {
    setError(null);
    try {
      const res = await adminFetch<{ url: string }>("/admin/payments/mp/authorize");
      window.location.href = res.url;
    } catch {
      setError("No se pudo iniciar la conexión con Mercado Pago.");
    }
  };

  return (
    <div>
      <h1>Mercado Pago</h1>
      {error && <p role="alert" style={{ color: "#8b0000" }}>{error}</p>}
      {status && (
        <p>
          Estado: {status.connected ? "Conectado" : "Sin conectar"}
          {status.mp_user_id ? ` (${status.mp_user_id})` : ""}
        </p>
      )}
      <button type="button" onClick={connect}>Conectar cuenta</button>
    </div>
  );
}
