import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { loadEnv } from "vite";
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  base: loadEnv(mode, ".", "VITE_").VITE_OFFLINE_DEMO === "true" ? "./" : "/",
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/benchmark/latest.json": "http://127.0.0.1:8000",
    },
  },
  test: { environment: "jsdom", setupFiles: ["./src/test-setup.ts"] },
}));
