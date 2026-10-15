import { Link, Outlet } from "react-router-dom";

export function AdminLayout() {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <nav style={{ width: 220, padding: 16, borderRight: "1px solid #ddd" }}>
        <strong>Turnos SaaS</strong>
        <ul style={{ listStyle: "none", padding: 0 }}>
          <li><Link to="/admin">Agenda</Link></li>
          <li><Link to="/admin/site-builder">Sitio</Link></li>
        </ul>
      </nav>
      <main style={{ flex: 1, padding: 24 }}>
        <Outlet />
      </main>
    </div>
  );
}
