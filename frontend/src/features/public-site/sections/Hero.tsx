export function Hero(props: { title?: string; cta?: string }) {
  return (
    <header style={{ padding: "48px 24px", textAlign: "center" }}>
      <h1 style={{ fontFamily: "var(--font)" }}>{props.title ?? "Bienvenido"}</h1>
      <p>{props.cta ?? "Reservá tu turno"}</p>
    </header>
  );
}
