import { useParams } from "react-router-dom";
import { BookingWidget } from "@/features/public-site/booking/BookingWidget";
import { applyTheme } from "@/features/public-site/theme/applyTheme";
import { sectionRegistry } from "@/features/public-site/registry";

const emptyConfig = {
  template: "minimal",
  theme: {
    primary: "#C9A24B",
    background: "#0F0F0F",
    font: "system-ui",
    radius: "lg",
  },
  sections: [
    { type: "hero", enabled: true, props: { title: "Tu negocio", cta: "Reservar" } },
    { type: "services", enabled: true, props: {} },
  ],
};

export function PublicSitePage() {
  const { slug } = useParams<{ slug: string }>();
  applyTheme(emptyConfig.theme);

  const sections = emptyConfig.sections.filter((s) => s.enabled);

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", color: "var(--fg)" }}>
      {sections.map((section) => {
        const Component = sectionRegistry[section.type];
        if (!Component) return null;
        return <Component key={section.type} {...section.props} />;
      })}
      <BookingWidget slug={slug ?? ""} />
    </div>
  );
}
