<template>
  <div class="min-h-screen bg-slate-100">
    <AppNavbar />
    <div class="mx-auto max-w-[1600px] p-6">
      <GraphCanvas />
    </div>
  </div>
</template>

<script setup lang="ts">
import AppNavbar from "../components/layout/AppNavbar.vue";
import GraphCanvas from "../components/graph/GraphCanvas.vue";
</script>
