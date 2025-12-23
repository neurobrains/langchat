import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { copyFileSync, existsSync } from "fs";
import { join, resolve } from "path";
import { fileURLToPath } from "url";

const __dirname = fileURLToPath(new URL(".", import.meta.url));

export default defineConfig({
  base: "/frontend/",
  plugins: [
    react(),
    {
      name: "copy-logo",
      closeBundle() {
        // Copy logo to dist after build
        try {
          // Try multiple possible paths
          const possiblePaths = [
            resolve(__dirname, "../../../../docs/public/logo-sidebar.png"),
            resolve(__dirname, "../../../docs/public/logo-sidebar.png"),
            resolve(__dirname, "../../../../../../docs/public/logo-sidebar.png"),
          ];
          
          let logoSource = null;
          for (const path of possiblePaths) {
            if (existsSync(path)) {
              logoSource = path;
              break;
            }
          }
          
          if (logoSource) {
            const logoDest = resolve(__dirname, "dist/logo-sidebar.png");
            copyFileSync(logoSource, logoDest);
            console.log("Logo copied successfully");
          } else {
            console.warn("Logo file not found, skipping copy");
          }
        } catch (e) {
          console.warn("Could not copy logo:", e);
        }
      },
    },
  ],
  server: {
    port: 5173,
    proxy: {
      // Dev-only proxy to FastAPI
      "/chat": "http://localhost:8000",
      "/health": "http://localhost:8000"
    }
  }
});


