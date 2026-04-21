<template>
  <section class="min-h-[520px] rounded-2xl border border-brand-900/10 bg-white p-5 shadow-sm md:p-6">
    <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
      <h2 class="text-base font-semibold text-brand-900 md:text-lg">Relationship Graph</h2>
      <span class="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
        Nodes {{ graphData?.nodes.length || 0 }} / Edges {{ graphData?.edges.length || 0 }}
      </span>
    </div>

    <div
      class="relative overflow-hidden rounded-xl border border-dashed border-brand-300 bg-gradient-to-br from-brand-50 to-slate-100"
    >
      <div v-if="!graphData || graphData.nodes.length === 0" class="flex min-h-[430px] items-center justify-center">
        <div class="text-center">
          <p class="text-lg font-semibold text-brand-800">等待图谱数据</p>
          <p class="mt-2 text-sm text-slate-500">上传 PDF/PPT 后将自动渲染知识图谱</p>
        </div>
      </div>

      <svg v-else :viewBox="`0 0 ${width} ${height}`" class="h-[480px] w-full">
        <line
          v-for="edge in edgeLines"
          :key="`${edge.source}-${edge.target}`"
          :x1="edge.x1"
          :y1="edge.y1"
          :x2="edge.x2"
          :y2="edge.y2"
          stroke="#5b88ff"
          :stroke-width="Math.min(6, 1 + edge.weight * 0.6)"
          stroke-opacity="0.55"
        />

        <g v-for="node in positionedNodes" :key="node.id">
          <circle
            :cx="node.x"
            :cy="node.y"
            :r="Math.min(24, 12 + (node.score || 1) * 0.8)"
            :fill="node.type === 'entity' ? '#1f4dca' : node.type === 'hybrid' ? '#7c3aed' : '#1e3f9f'"
            fill-opacity="0.88"
          />
          <text :x="node.x" :y="node.y + 32" text-anchor="middle" font-size="12" fill="#1f2937">
            {{ node.label }}
          </text>
        </g>
      </svg>
    </div>

    <div v-if="graphData" class="mt-4 grid gap-4 md:grid-cols-2">
      <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
        <h3 class="text-sm font-semibold text-slate-700">关键词 / 实体</h3>
        <p class="mt-2 text-xs text-slate-500">
          关键词: {{ graphData.keywords?.slice(0, 12).join(", ") || "-" }}
        </p>
        <p class="mt-2 text-xs text-slate-500">
          实体: {{ graphData.entities?.slice(0, 8).join(", ") || "-" }}
        </p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
        <h3 class="text-sm font-semibold text-slate-700">关系边（Top 8）</h3>
        <ul class="mt-2 space-y-1 text-xs text-slate-600">
          <li v-for="item in topEdges" :key="`${item.source}-${item.target}`">
            {{ item.source }} -> {{ item.target }} | {{ item.relation || "co_occurs" }} | w={{ item.weight ?? 1 }}
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useGraphStore } from "../../stores/graph";

const width = 960;
const height = 540;

const graphStore = useGraphStore();
const graphData = computed(() => graphStore.data);

const positionedNodes = computed(() => {
  if (!graphData.value) return [];
  const radius = Math.min(width, height) * 0.33;
  const centerX = width / 2;
  const centerY = height / 2;
  const total = Math.max(1, graphData.value.nodes.length);

  return graphData.value.nodes.map((node, index) => {
    const angle = (2 * Math.PI * index) / total;
    return {
      ...node,
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
    };
  });
});

const edgeLines = computed(() => {
  if (!graphData.value) return [];
  const map = new Map(positionedNodes.value.map((node) => [node.id, node]));
  return graphData.value.edges
    .map((edge) => {
      const source = map.get(edge.source);
      const target = map.get(edge.target);
      if (!source || !target) return null;
      return {
        source: edge.source,
        target: edge.target,
        x1: source.x,
        y1: source.y,
        x2: target.x,
        y2: target.y,
        weight: edge.weight ?? 1,
      };
    })
    .filter(Boolean) as Array<{
    source: string;
    target: string;
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    weight: number;
  }>;
});

const topEdges = computed(() => {
  if (!graphData.value) return [];
  return [...graphData.value.edges]
    .sort((a, b) => (b.weight ?? 1) - (a.weight ?? 1))
    .slice(0, 8);
});
</script>
