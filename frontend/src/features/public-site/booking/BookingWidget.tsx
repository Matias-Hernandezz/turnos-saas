import { useBookingFlow } from "@/features/public-site/booking/useBookingFlow";

export function BookingWidget({ slug }: { slug: string }) {
  const { step } = useBookingFlow();
  return (
    <aside
      style={{
        position: "sticky",
        bottom: 0,
        padding: 16,
        background: "var(--primary)",
        color: "#111",
      }}
    >
      Reservar — {slug} — paso: {step}
    </aside>
  );
}
