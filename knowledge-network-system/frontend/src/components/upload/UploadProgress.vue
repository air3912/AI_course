<template>
  <div>
    <div class="mb-2 flex items-center justify-between text-xs text-slate-500">
      <span>{{ label }}</span>
      <span>{{ progress }}%</span>
    </div>
    <div class="h-2 w-full overflow-hidden rounded-full bg-slate-200">
      <div
        class="h-full rounded-full bg-brand-600 transition-all duration-200"
        :style="{ width: `${progress}%` }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  progress: number;
  label: string;
}>();
</script>
