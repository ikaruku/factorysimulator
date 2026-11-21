import { defineConfig } from "vite";

export default defineConfig({
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/colyseus": {
        target: "http://localhost:2567",
        changeOrigin: true,
        ws: true,
        rewrite: (path) => path.replace(/^\/colyseus/, ""),
      },
    },
  },
});
