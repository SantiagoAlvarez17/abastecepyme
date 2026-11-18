import { request } from "./api-client";
import type { DashboardSummaryDTO } from "@/lib/types";

export const dashboardService = {
  getSummary: () => request<DashboardSummaryDTO>("GET", "/dashboard/summary"),
};
