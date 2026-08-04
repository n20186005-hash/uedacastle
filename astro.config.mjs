import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";

// Node 22 can load .env without an additional runtime dependency.
try {
  process.loadEnvFile();
} catch {
  // .env is optional in CI; environment variables may be supplied directly.
}

const site = process.env.SITE_URL ?? "https://ueda-castle-walk.example";

export default defineConfig({
  site,
  output: "static",
  trailingSlash: "always",
  vite: {
    plugins: [tailwindcss()],
  },
});
