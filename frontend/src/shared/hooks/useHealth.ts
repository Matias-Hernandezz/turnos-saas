import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/shared/api/client";
import type { HealthResponse } from "@/shared/api/types";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => apiFetch<HealthResponse>("/health"),
  });
}
