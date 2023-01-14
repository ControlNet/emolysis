import { createRouter, createWebHistory } from "vue-router"
import WelcomeView from "@/views/WelcomeView.vue";
import MainView from "@/views/MainView.vue";

export default createRouter({
    history: createWebHistory("/"),
    routes: [
        { path: "/", component: WelcomeView},
        { path: "/:mode/:videoId", component: MainView},
        { path: "/:mode/:videoId", component: MainView},
    ]
})
