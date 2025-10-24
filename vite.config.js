import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.svg"],
      manifest: {
        name: "EGOEJO",
        short_name: "EGOEJO",
        theme_color: "#00ffa3",
        background_color: "#030806",
        start_url: "/",
        display: "standalone",
        icons: [
          { src: "/favicon.svg", sizes: "64x64", type: "image/svg+xml", purpose: "any" }
        ]
      }
    })
  ]
});
