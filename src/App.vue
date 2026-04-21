<script setup>
import { computed, ref } from "vue";

const fileInputRef = ref(null);
const isDragging = ref(false);
const uploadProgress = ref(0);
const isUploading = ref(false);
const uploadedFile = ref(null);
const errorMessage = ref("");
let timer = null;

const acceptedExtensions = [".pdf", ".ppt", ".pptx"];

const progressLabel = computed(() => {
  if (!uploadedFile.value) return "未选择文件";
  if (isUploading.value) return `正在上传 ${uploadedFile.value.name}`;
  return `已上传 ${uploadedFile.value.name}`;
});

const resetUpload = () => {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
  uploadProgress.value = 0;
  isUploading.value = false;
};

const isValidType = (file) => {
  const lowerName = file.name.toLowerCase();
  return acceptedExtensions.some((ext) => lowerName.endsWith(ext));
};

const startUpload = (file) => {
  errorMessage.value = "";
  uploadedFile.value = file;
  resetUpload();
  isUploading.value = true;

  timer = setInterval(() => {
    uploadProgress.value += Math.floor(Math.random() * 15) + 8;
    if (uploadProgress.value >= 100) {
      uploadProgress.value = 100;
      isUploading.value = false;
      clearInterval(timer);
      timer = null;
    }
  }, 220);
};

const handleFile = (file) => {
  if (!file) return;
  if (!isValidType(file)) {
    errorMessage.value = "仅支持 PDF、PPT、PPTX 文件。";
    return;
  }
  startUpload(file);
};

const onFileChange = (event) => {
  const file = event.target.files?.[0];
  handleFile(file);
  event.target.value = "";
};

const onDrop = (event) => {
  event.preventDefault();
  isDragging.value = false;
  const file = event.dataTransfer.files?.[0];
  handleFile(file);
};

const onDragOver = (event) => {
  event.preventDefault();
  isDragging.value = true;
};

const onDragLeave = () => {
  isDragging.value = false;
};

const openFileDialog = () => {
  fileInputRef.value?.click();
};
</script>

<template>
  <div class="flex h-full flex-col bg-slate-100 text-slate-800">
    <header class="border-b border-brand-800/20 bg-brand-900 text-white shadow-lg">
      <div class="mx-auto flex h-16 max-w-[1600px] items-center px-5 md:px-8">
        <h1 class="text-lg font-semibold tracking-wide md:text-xl">课程知识网络分析系统</h1>
      </div>
    </header>

    <main class="mx-auto flex w-full max-w-[1600px] flex-1 gap-5 p-5 md:gap-6 md:p-6">
      <aside class="w-full rounded-2xl border border-brand-900/10 bg-white p-5 shadow-sm md:w-[340px]">
        <div class="mb-4">
          <h2 class="text-base font-semibold text-brand-900">文件上传</h2>
          <p class="mt-1 text-sm text-slate-500">拖拽或选择 PDF / PPT 文件</p>
        </div>

        <div
          class="cursor-pointer rounded-xl border-2 border-dashed p-6 text-center transition"
          :class="
            isDragging
              ? 'border-brand-500 bg-brand-50'
              : 'border-slate-300 bg-slate-50 hover:border-brand-400 hover:bg-brand-50/50'
          "
          @click="openFileDialog"
          @drop="onDrop"
          @dragover="onDragOver"
          @dragleave="onDragLeave"
        >
          <p class="text-sm font-medium text-slate-700">将文件拖拽到这里</p>
          <p class="mt-2 text-xs text-slate-500">或点击选择文件</p>
          <input
            ref="fileInputRef"
            type="file"
            class="hidden"
            accept=".pdf,.ppt,.pptx"
            @change="onFileChange"
          />
        </div>

        <div class="mt-5">
          <div class="mb-2 flex items-center justify-between text-xs text-slate-500">
            <span>{{ progressLabel }}</span>
            <span>{{ uploadProgress }}%</span>
          </div>
          <div class="h-2 w-full overflow-hidden rounded-full bg-slate-200">
            <div
              class="h-full rounded-full bg-brand-600 transition-all duration-200"
              :style="{ width: `${uploadProgress}%` }"
            />
          </div>
        </div>

        <p v-if="errorMessage" class="mt-3 text-sm text-red-600">{{ errorMessage }}</p>
      </aside>

      <section class="min-h-[480px] flex-1 rounded-2xl border border-brand-900/10 bg-white p-5 shadow-sm md:p-6">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-base font-semibold text-brand-900 md:text-lg">Relationship Graph</h2>
          <span class="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">Graph Area</span>
        </div>

        <div
          class="flex h-[calc(100%-2.5rem)] min-h-[420px] items-center justify-center rounded-xl border border-dashed border-brand-300 bg-gradient-to-br from-brand-50 to-slate-100"
        >
          <div class="text-center">
            <p class="text-lg font-semibold text-brand-800">关系图谱渲染容器</p>
            <p class="mt-2 text-sm text-slate-500">后续可在此接入 D3.js / ECharts / Cytoscape</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>
