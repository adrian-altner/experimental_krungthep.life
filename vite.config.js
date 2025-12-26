import { defineConfig } from "vite";
import path from "path";

export default defineConfig(({ mode }) => {
  const isDev = mode === "development";

  return {
    root: path.resolve(__dirname, "frontend"),
    build: {
      outDir: path.resolve(__dirname, "core/static/vite"),
      emptyOutDir: true,
      sourcemap: isDev,
      rollupOptions: {
        input: path.resolve(__dirname, "frontend/src/main.js"),
        output: {
          entryFileNames: "app.js",
          assetFileNames: (assetInfo) => {
            if (assetInfo.name && assetInfo.name.endsWith(".css")) {
              return "app.css";
            }
            return "assets/[name]-[hash][extname]";
          },
        },
      },
    },
  };
});
