import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  // Keep the variable name from the Vue CLI days (VUE_APP_API_URL), so .env,
  // the Dockerfile build arg and the README stay valid.
  envPrefix: ["VITE_", "VUE_APP_"],
  server: {
    port: 8080,
  },
});
