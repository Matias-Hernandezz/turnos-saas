import { useState } from "react";

export function PreviewFrame() {
  const [mode, setMode] = useState<"desktop" | "mobile">("mobile");
  const width = mode === "mobile" ? 390 : "100%";
  return (
    <div>
      <div style={{ marginBottom: 8 }}>
        <button type="button" onClick={() => setMode("mobile")}>Móvil</button>
        <button type="button" onClick={() => setMode("desktop")}>Desktop</button>
      </div>
      <div style={{ border: "1px solid #ccc", margin: "0 auto", width, minHeight: 480 }}>
        <p style={{ padding: 16 }}>Preview en vivo — pendiente sync con draft.</p>
      </div>
    </div>
  );
}
