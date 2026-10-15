import { useState } from "react";

export type BookingStep = "service" | "professional" | "slot" | "details" | "payment";

export function useBookingFlow() {
  const [step, setStep] = useState<BookingStep>("service");
  return { step, setStep };
}
