import { api } from "./api";
import type { GraphBuildResponse } from "../types/graph";

export async function buildGraph(text: string): Promise<GraphBuildResponse> {
  const { data } = await api.post<GraphBuildResponse>("/graph/build", { text });
  return data;
}
