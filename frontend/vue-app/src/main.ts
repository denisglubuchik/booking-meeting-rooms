import { createApp } from "vue";
import { createPinia } from "pinia";
import { VueQueryPlugin } from "@tanstack/vue-query";
import App from "./App.vue";
import router from "./app/router";
import "./styles.css";
import { useAuthStore } from "./features/auth/store";

async function bootstrap() {
  const app = createApp(App);
  const pinia = createPinia();
  app.use(pinia);
  app.use(VueQueryPlugin);

  const auth = useAuthStore();
  await auth.hydrate();

  app.use(router).mount("#app");
}

void bootstrap();
