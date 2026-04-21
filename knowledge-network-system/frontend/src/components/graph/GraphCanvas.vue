<template>
  <section class="min-h-[520px] rounded-2xl border border-brand-900/10 bg-white p-5 shadow-sm md:p-6">
    <div class="mb-4 flex flex-wrap items-center justify-between gap-2">
      <h2 class="text-base font-semibold text-brand-900 md:text-lg">知识关系图谱</h2>
      <span class="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
        Nodes {{ graphData?.nodes.length || 0 }} / Edges {{ graphData?.edges.length || 0 }}
      </span>
    </div>

    <div class="relative overflow-hidden rounded-xl border border-dashed border-brand-300 bg-gradient-to-br from-brand-50 to-slate-100">
      <div v-if="!graphData || graphData.nodes.length === 0" class="flex min-h-[430px] items-center justify-center">
        <div class="text-center">
          <p class="text-lg font-semibold text-brand-800">等待图谱数据</p>
          <p class="mt-2 text-sm text-slate-500">上传 PDF/PPT 后将自动解析并渲染知识网络</p>
        </div>
      </div>
      <div v-else ref="chartRef" class="h-[480px] w-full" />
    </div>

    <div v-if="graphData" class="mt-4 grid gap-4 md:grid-cols-2">
      <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
        <h3 class="text-sm font-semibold text-slate-700">关键词 / 实体</h3>
        <p class="mt-2 text-xs text-slate-500">关键词: {{ graphData.keywords?.slice(0, 12).join(", ") || "-" }}</p>
        <p class="mt-2 text-xs text-slate-500">实体: {{ graphData.entities?.slice(0, 8).join(", ") || "-" }}</p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-slate-50 p-3">
        <h3 class="text-sm font-semibold text-slate-700">关系边（Top 8）</h3>
        <ul class="mt-2 space-y-1 text-xs text-slate-600">
          <li v-for="item in topEdges" :key="`${item.source}-${item.target}-${item.relation}`">
            {{ item.source }} -> {{ item.target }} | {{ item.relation || "related_to" }} | w={{ item.weight ?? 1 }}
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";
import * as echarts from "echarts";
import { useGraphStore } from "../../stores/graph";

const graphStore = useGraphStore();
const graphData = computed(() => graphStore.data);

const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

const topEdges = computed(() => {
  if (!graphData.value) return [];
  return [...graphData.value.edges].sort((a, b) => (b.weight ?? 1) - (a.weight ?? 1)).slice(0, 8);
});

const typeToCategory = (type?: string) => {
  const t = (type || "keyword").toLowerCase();
  if (t === "entity") return "实体";
  if (t === "hybrid") return "混合";
  if (t === "topic") return "主题";
  if (t === "method") return "方法";
  if (t === "dataset") return "数据集";
  if (t === "paper") return "论文";
  if (t === "person") return "人物";
  if (t === "org") return "组织";
  if (t === "tool") return "工具";
  return "关键词";
};

const buildOption = () => {
  const data = graphData.value;
  if (!data) return null;

  const categories = Array.from(new Set(data.nodes.map((n) => typeToCategory(n.type)))).map((name) => ({ name }));
  const categoryIndex = new Map(categories.map((c, idx) => [c.name, idx]));

  const nodes = data.nodes.map((n) => {
    const score = n.score ?? 1;
    const size = Math.max(10, Math.min(42, 10 + score * 1.2));
    const categoryName = typeToCategory(n.type);
    return {
      id: n.id,
      name: n.label || n.id,
      value: score,
      symbolSize: size,
      category: categoryIndex.get(categoryName) ?? 0,
    };
  });

  const links = data.edges.map((e) => {
    const w = e.weight ?? 1;
    return {
      source: e.source,
      target: e.target,
      value: w,
      lineStyle: { width: Math.max(1, Math.min(6, 0.8 + w * 0.6)), opacity: 0.55 },
      label: { show: false },
    };
  });

  return {
    tooltip: {
      trigger: "item",
    },
    legend: [{ data: categories.map((c) => c.name) }],
    series: [
      {
        type: "graph",
        layout: "force",
        roam: true,
        draggable: true,
        data: nodes,
        links,
        categories,
        label: {
          show: true,
          position: "right",
          formatter: "{b}",
          color: "#0f172a",
          fontSize: 12,
        },
        force: {
          repulsion: 220,
          edgeLength: [60, 160],
          gravity: 0.08,
        },
        lineStyle: {
          color: "source",
          curveness: 0.18,
        },
        emphasis: {
          focus: "adjacency",
        },
      },
    ],
  };
};

const ensureChart = () => {
  if (!chartRef.value) return null;
  if (!chart) chart = echarts.init(chartRef.value);
  return chart;
};

const render = async () => {
  if (!graphData.value || graphData.value.nodes.length === 0) {
    if (chart) chart.clear();
    return;
  }

  await nextTick();
  const instance = ensureChart();
  const option = buildOption();
  if (!instance || !option) return;
  instance.setOption(option, { notMerge: true, lazyUpdate: true });
  instance.resize();
};

watch(graphData, () => {
  void render();
});

const onResize = () => {
  if (chart) chart.resize();
};

window.addEventListener("resize", onResize);

onBeforeUnmount(() => {
  window.removeEventListener("resize", onResize);
  if (chart) {
    chart.dispose();
    chart = null;
  }
});
</script>
