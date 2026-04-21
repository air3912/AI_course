import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import GraphView from "../views/GraphView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "home", component: HomeView },
    { path: "/graph", name: "graph", component: GraphView },
  ],
});

export default router;
