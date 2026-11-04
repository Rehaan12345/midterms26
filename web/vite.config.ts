import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "./",
  // MapLibre 6 loads its worker as an ES module; bundle it as one.
  worker: { format: "es" },
});
