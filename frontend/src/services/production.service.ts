import { request } from "./api-client";
import type { ProductionOrderDTO } from "@/lib/types";

export const productionService = {
  getOrder: () => request<ProductionOrderDTO>("GET", "/production-order"),
};