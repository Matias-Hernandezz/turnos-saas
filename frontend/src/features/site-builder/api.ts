import { apiFetch } from "@/shared/api/client";

export function fetchSiteDraft() {
  return apiFetch<{ draft_config: Record<string, unknown> }>("/admin/site/draft");
}
