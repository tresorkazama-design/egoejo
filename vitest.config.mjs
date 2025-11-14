import { defineConfig, defaultExclude } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    dir: "tests/unit",
    include: ["**/*.test.{js,jsx,ts,tsx}"],
    exclude: [
      ...defaultExclude,
      "**/*.spec.{js,jsx,ts,tsx}",
    ],
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/test/setup.js",
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      exclude: ["node_modules/", "src/test/", "**/*.config.*", "**/dist/"],
    },
  },
});
