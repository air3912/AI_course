import { defineStore } from "pinia";
import type { GraphBuildResponse } from "../types/graph";

export const useGraphStore = defineStore("graph", {
  state: () => ({
    data: null as GraphBuildResponse | null,
  }),
  actions: {
    setGraph(data: GraphBuildResponse) {
      this.data = data;
    },
    clear() {
      this.data = null;
    },
  },
});
