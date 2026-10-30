import { request } from "./api-client";
import type { DependencyDTO, ElementDTO, ElementType, GraphDTO } from "@/lib/types";

export const catalogService = {
  getGraph: () => request<GraphDTO>("GET", "/graph"),

  createElement: (input: { name: string; element_type: ElementType }) =>
    request<ElementDTO>("POST", "/elements", input),

  registerDependency: (input: DependencyDTO) =>
    request<DependencyDTO>("POST", "/dependencies", input),
};