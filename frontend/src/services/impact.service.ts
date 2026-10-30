import { request } from "./api-client";
import type { ImpactMode, ImpactResponseDTO } from "@/lib/types";

export const impactService = {
  analyze: (elementId: string, mode: ImpactMode) =>
    request<ImpactResponseDTO>("GET", `/impact/${encodeURIComponent(elementId)}?mode=${mode}`),
};