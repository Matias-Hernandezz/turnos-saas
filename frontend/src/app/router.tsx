import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AdminLayout } from "@/app/layouts/AdminLayout";
import { PublicLayout } from "@/app/layouts/PublicLayout";
import { BuilderPage } from "@/features/site-builder/BuilderPage";
import { PublicBookingPage } from "@/features/public-site/booking/PublicBookingPage";
import { PublicSitePage } from "@/features/public-site/PublicSitePage";

function AdminHome() {
  return <p>Panel admin — MVP en construcción</p>;
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/admin" replace />} />
        <Route path="/t/:slug" element={<PublicLayout />}>
          <Route index element={<PublicSitePage />} />
          <Route path="reserva/:publicCode" element={<PublicBookingPage />} />
        </Route>
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<AdminHome />} />
          <Route path="site-builder" element={<BuilderPage />} />
        </Route>
        <Route path="/super-admin" element={<p>Super admin — pendiente</p>} />
      </Routes>
    </BrowserRouter>
  );
}
