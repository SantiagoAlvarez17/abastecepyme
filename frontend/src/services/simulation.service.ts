import { request } from "./api-client";
import type { UnavailabilitySimulationDTO } from "@/lib/types";

export const simulationService = {
  simulateUnavailability: (elementIds: string[]) =>
    request<UnavailabilitySimulationDTO>("POST", "/simulations/unavailability", {
      element_ids: elementIds,
    }),
};
