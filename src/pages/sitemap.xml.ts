import type { APIRoute } from "astro";

const pages = ["", "history/", "highlights/", "routes/", "access/", "food/", "seasons/", "sakura/", "autumn/", "faq/", "credits/"];

export const GET: APIRoute = ({ site }) => {
  const base = site ?? new URL("https://ueda-castle-walk.example");
  const urls = pages.map((path) => `<url><loc>${new URL(path, base).toString()}</loc><changefreq>${path === "" ? "weekly" : "monthly"}</changefreq><priority>${path === "" ? "1.0" : "0.8"}</priority></url>`).join("");
  const body = `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls}</urlset>`;
  return new Response(body, { headers: { "Content-Type": "application/xml; charset=utf-8" } });
};
