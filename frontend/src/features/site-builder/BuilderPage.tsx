import { PreviewFrame } from "@/features/site-builder/preview/PreviewFrame";
import { TemplatePicker } from "@/features/site-builder/panels/TemplatePicker";
import { ThemePanel } from "@/features/site-builder/panels/ThemePanel";

export function BuilderPage() {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: 16, height: "calc(100vh - 48px)" }}>
      <div style={{ overflow: "auto", borderRight: "1px solid #ddd", paddingRight: 16 }}>
        <TemplatePicker />
        <ThemePanel />
      </div>
      <PreviewFrame />
    </div>
  );
}
