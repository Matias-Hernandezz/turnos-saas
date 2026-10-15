import type { CSSProperties } from "react";
import { Button } from "@/shared/ui/Button";
import { useBookingFlow } from "@/features/public-site/booking/useBookingFlow";

function formatSlotTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

function formatDateTime(iso: string) {
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    weekday: "short",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function BookingWidget({ slug }: { slug: string }) {
  const flow = useBookingFlow(slug);
  const {
    step,
    loading,
    error,
    services,
    professionals,
    slots,
    service,
    professional,
    day,
    setDay: setBookingDay,
    customerName,
    setCustomerName,
    customerEmail,
    setCustomerEmail,
    customerPhone,
    setCustomerPhone,
    booking,
    pickService,
    pickProfessional,
    pickSlot,
    goBack,
    submitBooking,
  } = flow;

  if (!slug) return null;

  const panelStyle: CSSProperties = {
    position: "sticky",
    bottom: 0,
    padding: 16,
    background: "var(--primary)",
    color: "#111",
    maxHeight: "45vh",
    overflowY: "auto",
  };

  const listBtn: CSSProperties = {
    display: "block",
    width: "100%",
    textAlign: "left",
    marginBottom: 8,
    padding: "10px 12px",
    borderRadius: 8,
    border: "1px solid rgba(0,0,0,0.15)",
    background: "#fff",
    cursor: "pointer",
  };

  return (
    <aside style={panelStyle} aria-label="Reservar turno">
      <strong>Reservar</strong>
      {error && (
        <p style={{ margin: "8px 0", color: "#8b0000", fontSize: 14 }} role="alert">
          {error}
        </p>
      )}
      {loading && <p style={{ margin: "8px 0", fontSize: 14 }}>Cargando…</p>}

      {step === "service" && (
        <div style={{ marginTop: 8 }}>
          <p style={{ margin: "0 0 8px", fontSize: 14 }}>Elegí un servicio</p>
          {services.map((s) => (
            <button key={s.id} type="button" style={listBtn} onClick={() => pickService(s)}>
              {s.name} · {s.duration_minutes} min
            </button>
          ))}
        </div>
      )}

      {step === "professional" && (
        <div style={{ marginTop: 8 }}>
          <Button onClick={goBack}>Volver</Button>
          <p style={{ margin: "8px 0", fontSize: 14 }}>Profesional</p>
          {professionals.map((p) => (
            <button key={p.id} type="button" style={listBtn} onClick={() => pickProfessional(p)}>
              {p.name}
            </button>
          ))}
        </div>
      )}

      {step === "slot" && service && professional && (
        <div style={{ marginTop: 8 }}>
          <Button onClick={goBack}>Volver</Button>
          <p style={{ margin: "8px 0", fontSize: 13 }}>
            {service.name} con {professional.name}
          </p>
          <label style={{ fontSize: 14 }}>
            Día{" "}
            <input
              type="date"
              value={day}
              onChange={(e) => setBookingDay(e.target.value)}
              style={{ marginLeft: 8 }}
            />
          </label>
          <div style={{ marginTop: 8 }}>
            {slots.length === 0 && !loading && (
              <p style={{ fontSize: 14 }}>No hay horarios ese día.</p>
            )}
            {slots.map((s) => (
              <button
                key={s.starts_at}
                type="button"
                style={listBtn}
                onClick={() => pickSlot(s)}
              >
                {formatSlotTime(s.starts_at)}
              </button>
            ))}
          </div>
        </div>
      )}

      {step === "details" && slot && (
        <div style={{ marginTop: 8 }}>
          <Button onClick={goBack}>Volver</Button>
          <p style={{ margin: "8px 0", fontSize: 14 }}>{formatDateTime(slot.starts_at)}</p>
          <label style={{ display: "block", fontSize: 14, marginBottom: 8 }}>
            Email
            <input
              type="email"
              value={customerEmail}
              onChange={(e) => setCustomerEmail(e.target.value)}
              style={{ display: "block", width: "100%", marginTop: 4, padding: 8 }}
              autoComplete="email"
              required
            />
          </label>
          <label style={{ display: "block", fontSize: 14, marginBottom: 8 }}>
            Nombre
            <input
              type="text"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              style={{ display: "block", width: "100%", marginTop: 4, padding: 8 }}
              autoComplete="name"
            />
          </label>
          <label style={{ display: "block", fontSize: 14, marginBottom: 8 }}>
            Teléfono (opcional)
            <input
              type="tel"
              value={customerPhone}
              onChange={(e) => setCustomerPhone(e.target.value)}
              style={{ display: "block", width: "100%", marginTop: 4, padding: 8 }}
              autoComplete="tel"
            />
          </label>
          <Button onClick={() => submitBooking()} disabled={loading}>
            Confirmar reserva
          </Button>
        </div>
      )}

      {step === "confirm" && booking && (
        <div style={{ marginTop: 8 }}>
          <p style={{ margin: 0, fontWeight: 600 }}>¡Listo!</p>
          <p style={{ margin: "8px 0", fontSize: 14 }}>
            Turno: {formatDateTime(booking.starts_at)}
          </p>
          <p style={{ margin: "8px 0", fontSize: 13 }}>
            Código: <code>{booking.public_code}</code>
          </p>
          <p style={{ margin: 0, fontSize: 12, opacity: 0.85 }}>
            Revisá tu email para el enlace de cancelación. Hold hasta{" "}
            {formatDateTime(booking.hold_expires_at)}.
          </p>
        </div>
      )}
    </aside>
  );
}
