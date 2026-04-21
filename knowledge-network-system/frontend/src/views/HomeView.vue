<template>
  <div class="min-h-screen bg-slate-100 text-slate-800">
    <AppNavbar />
    <main class="mx-auto flex w-full max-w-[1600px] gap-6 p-5 md:p-6">
      <section class="w-full md:w-[340px]">
        <FileDropzone />
      </section>
      <section class="flex-1">
        <GraphCanvas />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import AppNavbar from "../components/layout/AppNavbar.vue";
import FileDropzone from "../components/upload/FileDropzone.vue";
import GraphCanvas from "../components/graph/GraphCanvas.vue";
</script>
