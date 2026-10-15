import { useCallback, useEffect, useState, type FormEvent } from "react";
import { Navigate } from "react-router-dom";
import { createTimeOff, deleteTimeOff, fetchTimeOff, type TimeOffRow } from "@/features/admin/adminApi";
import { getAccessToken } from "@/shared/auth/token";

export function TimeOffPage() {
  const token = getAccessToken();
  const [rows, setRows] = useState<TimeOffRow[]>([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    fetchTimeOff()
      .then(setRows)
      .catch(() => setError("No se pudieron cargar los bloqueos."));
  }, []);

  useEffect(() => {
    if (!token) return;
    load();
  }, [token, load]);

  if (!token) return <Navigate to="/admin/login" replace />;

  const onCreate = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await createTimeOff({
        start_date: startDate,
        end_date: endDate,
        reason: reason.trim() || undefined,
      });
      setStartDate("");
      setEndDate("");
      setReason("");
      load();
    } catch {
      setError("No se pudo crear el bloqueo.");
    }
  };

  const onDelete = async (id: string) => {
    try {
      await deleteTimeOff(id);
      load();
    } catch {
      setError("No se pudo eliminar.");
    }
  };

  return (
    <div>
      <h1>Bloqueos de agenda</h1>
      {error && <p role="alert" style={{ color: "#8b0000" }}>{error}</p>}
      <form onSubmit={onCreate} style={{ marginBottom: 24, maxWidth: 400 }}>
        <p style={{ fontSize: 14 }}>Bloqueo para todo el negocio (sin profesional).</p>
        <label style={{ display: "block", marginBottom: 8 }}>
          Desde
          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required />
        </label>
        <label style={{ display: "block", marginBottom: 8 }}>
          Hasta
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} required />
        </label>
        <label style={{ display: "block", marginBottom: 8 }}>
          Motivo
          <input type="text" value={reason} onChange={(e) => setReason(e.target.value)} style={{ width: "100%" }} />
        </label>
        <button type="submit">Agregar bloqueo</button>
      </form>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {rows.map((r) => (
          <li key={r.id} style={{ marginBottom: 8, padding: 8, border: "1px solid #ccc" }}>
            {r.start_date} — {r.end_date}
            {r.reason ? ` · ${r.reason}` : ""}
            <button type="button" onClick={() => onDelete(r.id)} style={{ marginLeft: 8 }}>
              Eliminar
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
