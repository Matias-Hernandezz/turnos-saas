import { apiFetch } from "@/shared/api/client";

export type PublicService = {
  id: string;
  name: string;
  duration_minutes: number;
  price_cents: number;
  is_active: boolean;
};

export type PublicProfessional = {
  id: string;
  name: string;
  is_active: boolean;
};

export type PublicSlot = {
  professional_id: string;
  starts_at: string;
  ends_at: string;
};

export type SlotsResponse = {
  day: string;
  service_id: string;
  slots: PublicSlot[];
};

export type BookingCreated = {
  id: string;
  public_code: string;
  status: string;
  starts_at: string;
  ends_at: string;
  hold_expires_at: string;
};

export function fetchPublicServices(slug: string) {
  return apiFetch<PublicService[]>(`/public/${encodeURIComponent(slug)}/services`);
}

export function fetchPublicProfessionals(slug: string) {
  return apiFetch<PublicProfessional[]>(`/public/${encodeURIComponent(slug)}/professionals`);
}

export function fetchPublicSlots(
  slug: string,
  params: { service_id: string; day: string; professional_id: string },
) {
  const q = new URLSearchParams({
    service_id: params.service_id,
    day: params.day,
    professional_id: params.professional_id,
  });
  return apiFetch<SlotsResponse>(`/public/${encodeURIComponent(slug)}/slots?${q}`);
}

export type PublicBookingStatus = {
  slug: string;
  status: string;
  starts_at: string;
  ends_at: string;
  public_code: string;
};

export function fetchPublicBooking(slug: string, publicCode: string) {
  return apiFetch<PublicBookingStatus>(
    `/public/${encodeURIComponent(slug)}/bookings/${encodeURIComponent(publicCode)}`,
  );
}

export function createBookingCheckout(slug: string, publicCode: string) {
  return apiFetch<{ init_point: string; amount_cents: number }>(
    `/public/${encodeURIComponent(slug)}/bookings/${encodeURIComponent(publicCode)}/checkout`,
    { method: "POST" },
  );
}

export function cancelPublicBooking(slug: string, publicCode: string) {
  return apiFetch<BookingCreated>(
    `/public/${encodeURIComponent(slug)}/bookings/${encodeURIComponent(publicCode)}/cancel`,
    { method: "POST" },
  );
}

export function createPublicBooking(
  slug: string,
  body: {
    service_id: string;
    professional_id: string;
    starts_at: string;
    customer_name: string;
    customer_email?: string;
    customer_phone?: string;
  },
) {
  return apiFetch<BookingCreated>(`/public/${encodeURIComponent(slug)}/bookings`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
