import { useCallback, useEffect, useMemo, useState } from "react";
import { Navigate } from "react-router-dom";
import { AdminBooking, cancelAdminBooking, fetchAdminBookings } from "@/features/admin/adminApi";
import { getAccessToken } from "@/shared/auth/token";

function isoDate(d: Date) {
  return d.toISOString().slice(0, 10);
}

function startOfWeekMonday(d: Date) {
  const copy = new Date(d);
  const day = copy.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  copy.setDate(copy.getDate() + diff);
  copy.setHours(0, 0, 0, 0);
  return copy;
}

function addDays(d: Date, n: number) {
  const copy = new Date(d);
  copy.setDate(copy.getDate() + n);
  return copy;
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

const dayLabels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];

export function AgendaPage() {
  const token = getAccessToken();
  const [weekStart, setWeekStart] = useState(() => startOfWeekMonday(new Date()));
  const [bookings, setBookings] = useState<AdminBooking[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const fromDate = isoDate(weekStart);
  const toDate = isoDate(addDays(weekStart, 6));

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    fetchAdminBookings(fromDate, toDate)
      .then((res) => setBookings(res.bookings))
      .catch(() => setError("No se pudo cargar la agenda."))
      .finally(() => setLoading(false));
  }, [fromDate, toDate]);

  useEffect(() => {
    if (!token) return;
    load();
  }, [token, load]);

  const byDay = useMemo(() => {
    const map = new Map<string, AdminBooking[]>();
    for (let i = 0; i < 7; i++) {
      map.set(isoDate(addDays(weekStart, i)), []);
    }
    for (const b of bookings) {
      const key = b.starts_at.slice(0, 10);
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(b);
    }
    for (const list of map.values()) {
      list.sort((a, b) => a.starts_at.localeCompare(b.starts_at));
    }
    return map;
  }, [bookings, weekStart]);

  if (!token) {
    return <Navigate to="/admin/login" replace />;
  }

  const onCancel = async (id: string) => {
    try {
      await cancelAdminBooking(id);
      load();
    } catch {
      setError("No se pudo cancelar el turno.");
    }
  };

  return (
    <div>
      <header style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
        <button type="button" onClick={() => setWeekStart(addDays(weekStart, -7))}>
          ← Semana anterior
        </button>
        <strong>
          {fromDate} — {toDate}
        </strong>
        <button type="button" onClick={() => setWeekStart(addDays(weekStart, 7))}>
          Semana siguiente →
        </button>
      </header>
      {loading && <p>Cargando…</p>}
      {error && <p role="alert" style={{ color: "#8b0000" }}>{error}</p>}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(7, 1fr)",
          gap: 8,
          alignItems: "start",
        }}
      >
        {Array.from({ length: 7 }, (_, i) => {
          const day = addDays(weekStart, i);
          const key = isoDate(day);
          const items = byDay.get(key) ?? [];
          return (
            <section
              key={key}
              style={{ border: "1px solid #ccc", borderRadius: 8, padding: 8, minHeight: 120 }}
            >
              <h2 style={{ fontSize: 14, margin: "0 0 8px" }}>
                {dayLabels[i]} {day.getDate()}
              </h2>
              {items.length === 0 && (
                <p style={{ fontSize: 12, color: "#666", margin: 0 }}>Sin turnos</p>
              )}
              {items.map((b) => (
                <article
                  key={b.id}
                  style={{
                    fontSize: 12,
                    marginBottom: 8,
                    padding: 6,
                    background: "#f5f5f5",
                    borderRadius: 4,
                  }}
                >
                  <div>
                    <strong>{formatTime(b.starts_at)}</strong> · {b.service_name}
                  </div>
                  <div>{b.customer_name ?? "—"}</div>
                  <div style={{ color: "#444" }}>{b.status}</div>
                  {(b.status === "held" || b.status === "confirmed") && (
                    <button type="button" onClick={() => onCancel(b.id)} style={{ marginTop: 4 }}>
                      Cancelar
                    </button>
                  )}
                </article>
              ))}
            </section>
          );
        })}
      </div>
    </div>
  );
}
