import { adminFetch } from "@/shared/api/adminClient";

export type AdminBooking = {
  id: string;
  service_name: string;
  professional_name: string | null;
  customer_name: string | null;
  starts_at: string;
  ends_at: string;
  status: string;
};

export type AdminBookingsResponse = {
  from_date: string;
  to_date: string;
  bookings: AdminBooking[];
};

export function login(email: string, password: string, tenantSlug?: string) {
  return adminFetch<{ access_token: string }>("/auth/login", {
    method: "POST",
    body: JSON.stringify({
      email,
      password,
      tenant_slug: tenantSlug || undefined,
    }),
  });
}

export function fetchAdminBookings(fromDate: string, toDate: string) {
  const q = new URLSearchParams({ from_date: fromDate, to_date: toDate });
  return adminFetch<AdminBookingsResponse>(`/admin/bookings?${q}`);
}

export function cancelAdminBooking(id: string) {
  return adminFetch<AdminBooking>(`/admin/bookings/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ status: "cancelled" }),
  });
}
