import fs from "node:fs";
import path from "node:path";
import { defineConfig, type Plugin } from "vite";

const CONTENT_ROOT = path.resolve(__dirname, "../../content");

const MIME_BY_EXT: Record<string, string> = {
  ".glb": "model/gltf-binary",
  ".gltf": "model/gltf+json",
  ".json": "application/json",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".webp": "image/webp",
  ".svg": "image/svg+xml",
};

/** Serves the repository-root content/ directory at /content in dev and copies it on build. */
function contentDirPlugin(): Plugin {
  return {
    name: "factory-simulator-content-dir",
    configureServer(server) {
      server.middlewares.use("/content", (req, res, next) => {
        const cleanUrl = (req.url ?? "/").split("?")[0] ?? "/";
        const resolved = path.resolve(CONTENT_ROOT, `.${cleanUrl}`);
        if (!resolved.startsWith(CONTENT_ROOT) || !fs.existsSync(resolved)) {
          next();
          return;
        }
        const stat = fs.statSync(resolved);
        if (!stat.isFile()) {
          next();
          return;
        }
        const ext = path.extname(resolved).toLowerCase();
        res.setHeader("Content-Type", MIME_BY_EXT[ext] ?? "application/octet-stream");
        res.setHeader("Cache-Control", "no-store");
        fs.createReadStream(resolved).pipe(res);
      });
    },
    closeBundle() {
      if (!fs.existsSync(CONTENT_ROOT)) return;
      const distContent = path.resolve(__dirname, "dist/content");
      fs.cpSync(CONTENT_ROOT, distContent, { recursive: true });
    },
  };
}

export default defineConfig({
  plugins: [contentDirPlugin()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/colyseus": {
        target: "http://localhost:2567",
        changeOrigin: true,
        ws: true,
        rewrite: (reqPath) => reqPath.replace(/^\/colyseus/, ""),
      },
    },
  },
});
