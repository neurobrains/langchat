import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "/frontend/",
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Dev-only proxy to FastAPI
      "/chat": "http://localhost:8000",
      "/health": "http://localhost:8000"
    }
  }
});


