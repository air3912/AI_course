<template>
  <aside class="rounded-2xl border border-brand-900/10 bg-white p-5 shadow-sm">
    <div class="mb-4">
      <h2 class="text-base font-semibold text-brand-900">文件上传</h2>
      <p class="mt-1 text-sm text-slate-500">支持 PDF / PPT / PPTX，上传后自动解析并生成图谱</p>
    </div>

    <div
      class="cursor-pointer rounded-xl border-2 border-dashed p-6 text-center transition"
      :class="
        dragging
          ? 'border-brand-500 bg-brand-50'
          : 'border-slate-300 bg-slate-50 hover:border-brand-400 hover:bg-brand-50/50'
      "
      @click="triggerSelect"
      @dragover.prevent="dragging = true"
      @dragleave="dragging = false"
      @drop.prevent="onDrop"
    >
      <p class="text-sm font-medium text-slate-700">拖拽文件到这里</p>
      <p class="mt-2 text-xs text-slate-500">或点击选择文件</p>
      <input
        ref="inputRef"
        type="file"
        class="hidden"
        accept=".pdf,.ppt,.pptx"
        @change="onChange"
      />
    </div>

    <UploadProgress class="mt-5" :progress="uploadStore.progress" :label="statusLabel" />

    <div class="mt-4 space-y-2 text-xs">
      <div class="flex items-center justify-between">
        <span class="text-slate-500">上传状态</span>
        <span class="font-medium" :class="stageClass(uploadStageStatus)">{{ uploadStageStatus }}</span>
      </div>
      <div class="flex items-center justify-between">
        <span class="text-slate-500">解析状态</span>
        <span class="font-medium" :class="stageClass(parseStageStatus)">{{ parseStageStatus }}</span>
      </div>
      <div class="flex items-center justify-between">
        <span class="text-slate-500">图谱生成状态</span>
        <span class="font-medium" :class="stageClass(graphStageStatus)">{{ graphStageStatus }}</span>
      </div>
    </div>

    <div v-if="uploadStore.textLength > 0" class="mt-4 rounded-lg bg-slate-50 p-3 text-xs text-slate-600">
      <p>提取文本长度: {{ uploadStore.textLength }}</p>
      <p class="mt-1">文档ID: {{ uploadStore.documentId }} | 快照ID: {{ uploadStore.graphSnapshotId }}</p>
      <p class="mt-2 line-clamp-4">文本预览: {{ uploadStore.extractedTextPreview }}</p>
    </div>

    <p v-if="uploadStore.errorMessage" class="mt-3 text-sm text-red-600">{{ uploadStore.errorMessage }}</p>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { AxiosError } from "axios";
import UploadProgress from "./UploadProgress.vue";
import { uploadAndProcessFile } from "../../services/upload";
import { useUploadStore } from "../../stores/upload";
import { useGraphStore } from "../../stores/graph";

const inputRef = ref<HTMLInputElement | null>(null);
const dragging = ref(false);
const uploadStore = useUploadStore();
const graphStore = useGraphStore();

const statusLabel = computed(() => {
  if (!uploadStore.filename) return "未选择文件";
  if (uploadStore.status === "uploading") return `正在上传 ${uploadStore.filename}`;
  if (uploadStore.status === "parsing") return `正在解析 ${uploadStore.filename}`;
  if (uploadStore.status === "generating") return `正在生成图谱 ${uploadStore.filename}`;
  if (uploadStore.status === "done") return `处理完成 ${uploadStore.filename}`;
  if (uploadStore.status === "error") return `处理失败 ${uploadStore.filename}`;
  return uploadStore.filename;
});

const uploadStageStatus = computed(() => {
  if (uploadStore.status === "error") return "失败";
  if (uploadStore.status === "idle") return "待处理";
  if (uploadStore.status === "uploading") return "进行中";
  return "已完成";
});

const parseStageStatus = computed(() => {
  if (uploadStore.parseStatus === "failed") return "失败";
  if (uploadStore.parseStatus === "completed") return "已完成";
  if (uploadStore.parseStatus === "processing") return "进行中";
  return "待处理";
});

const graphStageStatus = computed(() => {
  if (uploadStore.graphStatus === "failed") return "失败";
  if (uploadStore.graphStatus === "completed") return "已完成";
  if (uploadStore.graphStatus === "processing") return "进行中";
  return "待处理";
});

const stageClass = (status: string): string => {
  if (status === "失败") return "text-red-600";
  if (status === "已完成") return "text-emerald-600";
  if (status === "进行中") return "text-brand-700";
  return "text-slate-500";
};

const validExt = (name: string): boolean => {
  const lower = name.toLowerCase();
  return [".pdf", ".ppt", ".pptx"].some((ext) => lower.endsWith(ext));
};

const extractErrorMessage = (error: unknown): string => {
  if (error instanceof AxiosError) {
    return error.response?.data?.detail || error.message || "请求失败";
  }
  return "处理失败，请重试。";
};

const handle = async (file?: File) => {
  if (!file) return;
  if (!validExt(file.name)) {
    uploadStore.reset();
    uploadStore.status = "error";
    uploadStore.errorMessage = "仅支持 PDF、PPT、PPTX 文件。";
    return;
  }

  uploadStore.reset();
  graphStore.clear();
  uploadStore.filename = file.name;
  uploadStore.status = "uploading";
  uploadStore.parseStatus = "idle";
  uploadStore.graphStatus = "idle";

  try {
    const data = await uploadAndProcessFile(file, (percent) => {
      uploadStore.progress = percent;
      if (percent >= 100 && uploadStore.status === "uploading") {
        uploadStore.status = "parsing";
        uploadStore.parseStatus = "processing";
        uploadStore.graphStatus = "processing";
      }
    });

    uploadStore.status = "generating";
    uploadStore.parseStatus = data.parse_status === "completed" ? "completed" : "failed";
    uploadStore.graphStatus = data.graph_status === "completed" ? "completed" : "failed";
    uploadStore.textLength = data.text_length;
    uploadStore.extractedTextPreview = data.extracted_text_preview;
    uploadStore.documentId = data.document_id;
    uploadStore.graphSnapshotId = data.graph_snapshot_id;
    uploadStore.progress = 100;

    graphStore.setGraph({
      nodes: data.nodes,
      edges: data.edges,
      keywords: data.keywords,
      entities: data.entities,
      stats: {
        node_count: data.nodes.length,
        edge_count: data.edges.length,
        keyword_count: data.keywords.length,
        entity_count: data.entities.length,
      },
    });
    uploadStore.status = "done";
  } catch (error) {
    uploadStore.status = "error";
    uploadStore.parseStatus = "failed";
    uploadStore.graphStatus = "failed";
    uploadStore.errorMessage = extractErrorMessage(error);
  }
};

const triggerSelect = () => inputRef.value?.click();

const onChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  void handle(target.files?.[0]);
  target.value = "";
};

const onDrop = (event: DragEvent) => {
  dragging.value = false;
  void handle(event.dataTransfer?.files?.[0]);
};
</script>
