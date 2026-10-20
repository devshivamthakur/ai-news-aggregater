import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    // Dev-only proxy that mirrors the `rewrites` rule the old next.config.mjs
    // provided, so a relative `/api/...` call works against the backend.
    proxy: {
      "/api": {
        target: process.env.VITE_PROXY_TARGET || "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: 4173,
  },
  build: {
    outDir: "dist",
    sourcemap: true,
    // Keep the vendor bundle from swallowing everything so route chunks stay
    // small — the app lazy-loads each page.
    chunkSizeWarningLimit: 700,
  },
});
