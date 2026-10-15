import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Button } from "@/shared/ui/Button";
import {
  cancelPublicBooking,
  fetchPublicBooking,
  type PublicBookingStatus,
} from "@/features/public-site/booking/publicApi";

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

export function PublicBookingPage() {
  const { slug, publicCode } = useParams<{ slug: string; publicCode: string }>();
  const [booking, setBooking] = useState<PublicBookingStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    if (!slug || !publicCode) return;
    setLoading(true);
    fetchPublicBooking(slug, publicCode)
      .then(setBooking)
      .catch(() => setError("No encontramos esta reserva."))
      .finally(() => setLoading(false));
  }, [slug, publicCode]);

  const onCancel = async () => {
    if (!slug || !publicCode) return;
    setCancelling(true);
    setError(null);
    try {
      await cancelPublicBooking(slug, publicCode);
      setBooking((b) => (b ? { ...b, status: "cancelled" } : b));
    } catch {
      setError("No se pudo cancelar. Puede que el turno ya no esté activo.");
    } finally {
      setCancelling(false);
    }
  };

  if (loading) return <p style={{ padding: 24 }}>Cargando…</p>;
  if (error && !booking) return <p style={{ padding: 24 }} role="alert">{error}</p>;
  if (!booking) return null;

  const canCancel = booking.status === "held" || booking.status === "confirmed";

  return (
    <main style={{ padding: 24, maxWidth: 480 }}>
      <h1>Tu reserva</h1>
      <p>Estado: <strong>{booking.status}</strong></p>
      <p>{formatDateTime(booking.starts_at)}</p>
      {error && <p role="alert" style={{ color: "#8b0000" }}>{error}</p>}
      {canCancel && (
        <Button onClick={onCancel} disabled={cancelling}>
          Cancelar turno
        </Button>
      )}
    </main>
  );
}
