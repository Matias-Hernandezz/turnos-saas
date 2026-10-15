import { useSiteDraftStore } from "@/features/site-builder/store";

const templates = ["minimal", "elegante", "bold"];

export function TemplatePicker() {
  const { template, setTemplate } = useSiteDraftStore();
  return (
    <section>
      <h3>Plantilla</h3>
      {templates.map((t) => (
        <button key={t} type="button" onClick={() => setTemplate(t)} disabled={t === template}>
          {t}
        </button>
      ))}
    </section>
  );
}
