import { useCallback, useEffect, useState } from "react";
import {
  BookingCreated,
  PublicProfessional,
  PublicService,
  PublicSlot,
  createPublicBooking,
  fetchPublicProfessionals,
  fetchPublicServices,
  fetchPublicSlots,
} from "@/features/public-site/booking/publicApi";

export type BookingStep = "service" | "professional" | "slot" | "details" | "confirm";

function defaultDay(): string {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toISOString().slice(0, 10);
}

export function useBookingFlow(slug: string) {
  const [step, setStep] = useState<BookingStep>("service");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [services, setServices] = useState<PublicService[]>([]);
  const [professionals, setProfessionals] = useState<PublicProfessional[]>([]);
  const [slots, setSlots] = useState<PublicSlot[]>([]);

  const [service, setService] = useState<PublicService | null>(null);
  const [professional, setProfessional] = useState<PublicProfessional | null>(null);
  const [day, setDay] = useState(defaultDay);
  const [slot, setSlot] = useState<PublicSlot | null>(null);
  const [customerName, setCustomerName] = useState("");
  const [customerPhone, setCustomerPhone] = useState("");
  const [booking, setBooking] = useState<BookingCreated | null>(null);

  const resetError = useCallback(() => setError(null), []);

  useEffect(() => {
    if (!slug || step !== "service") return;
    setLoading(true);
    resetError();
    fetchPublicServices(slug)
      .then(setServices)
      .catch(() => setError("No pudimos cargar los servicios."))
      .finally(() => setLoading(false));
  }, [slug, step, resetError]);

  useEffect(() => {
    if (!slug || step !== "professional") return;
    setLoading(true);
    resetError();
    fetchPublicProfessionals(slug)
      .then(setProfessionals)
      .catch(() => setError("No pudimos cargar los profesionales."))
      .finally(() => setLoading(false));
  }, [slug, step, resetError]);

  useEffect(() => {
    if (!slug || step !== "slot" || !service || !professional) return;
    setLoading(true);
    resetError();
    fetchPublicSlots(slug, {
      service_id: service.id,
      day,
      professional_id: professional.id,
    })
      .then((res) => setSlots(res.slots))
      .catch(() => setError("No pudimos cargar los horarios."))
      .finally(() => setLoading(false));
  }, [slug, step, service, professional, day, resetError]);

  const pickService = (s: PublicService) => {
    setService(s);
    setProfessional(null);
    setSlot(null);
    setStep("professional");
  };

  const pickProfessional = (p: PublicProfessional) => {
    setProfessional(p);
    setSlot(null);
    setStep("slot");
  };

  const pickSlot = (s: PublicSlot) => {
    setSlot(s);
    setStep("details");
  };

  const goBack = () => {
    resetError();
    if (step === "professional") setStep("service");
    else if (step === "slot") setStep("professional");
    else if (step === "details") setStep("slot");
  };

  const submitBooking = async () => {
    if (!service || !professional || !slot || !customerName.trim()) {
      setError("Completá tu nombre para confirmar.");
      return;
    }
    setLoading(true);
    resetError();
    try {
      const created = await createPublicBooking(slug, {
        service_id: service.id,
        professional_id: professional.id,
        starts_at: slot.starts_at,
        customer_name: customerName.trim(),
        customer_phone: customerPhone.trim() || undefined,
      });
      setBooking(created);
      setStep("confirm");
    } catch {
      setError("Ese horario ya no está disponible. Elegí otro.");
      setStep("slot");
      setSlot(null);
    } finally {
      setLoading(false);
    }
  };

  return {
    step,
    setStep,
    loading,
    error,
    services,
    professionals,
    slots,
    service,
    professional,
    day,
    setDay,
    slot,
    customerName,
    setCustomerName,
    customerPhone,
    setCustomerPhone,
    booking,
    pickService,
    pickProfessional,
    pickSlot,
    goBack,
    submitBooking,
  };
}
