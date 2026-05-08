import { createApp } from "vue";
import { createPinia } from "pinia";
import { VueQueryPlugin } from "@tanstack/vue-query";
import App from "./App.vue";
import router from "./app/router";
import "./styles.css";
import { useAuthStore } from "./features/auth/store";
import { i18n } from "./shared/i18n";

async function bootstrap() {
  const app = createApp(App);
  const pinia = createPinia();
  app.use(pinia);
  app.use(i18n);
  app.use(VueQueryPlugin, {
    queryClientConfig: {
      defaultOptions: {
        queries: {
          staleTime: 5 * 60 * 1000,
          refetchOnWindowFocus: false,
          refetchOnMount: false,
        },
      },
    },
  });

  const auth = useAuthStore();
  await auth.hydrate();

  app.use(router).mount("#app");
}

void bootstrap();
