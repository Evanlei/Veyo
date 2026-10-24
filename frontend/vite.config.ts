import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
    {
      name: "demo-page-metadata",
      transformIndexHtml(html) {
        return mode === "demo"
          ? html
              .replace(
                "<title>Veyo — Attention Studio</title>",
                "<title>Veyo — Recorded Attention Demo</title>",
              )
              .replace(
                "See what stands out. Analyze predicted attention, compare creative revisions, and make more informed design decisions with Veyo.",
                "Explore real recorded DeepGaze IIE heatmaps, annotated sample ads, and before-and-after comparisons in Veyo's public demo.",
              )
          : html;
      },
    },
  ],
  server: { proxy: mode === "demo" ? undefined : { "/api": "http://127.0.0.1:8000" } },
  build: { sourcemap: false, outDir: mode === "demo" ? "demo-dist" : "dist" },
  test: { environment: "node", include: ["src/**/*.test.ts"] },
}));
