type ThemeJson = {
  primary: string;
  background: string;
  font: string;
  radius: string;
};

export function applyTheme(theme: ThemeJson) {
  const root = document.documentElement;
  root.style.setProperty("--primary", theme.primary);
  root.style.setProperty("--bg", theme.background);
  root.style.setProperty("--fg", "#f5f5f5");
  root.style.setProperty("--font", theme.font);
  root.style.setProperty("--radius", theme.radius === "lg" ? "12px" : "6px");
}
