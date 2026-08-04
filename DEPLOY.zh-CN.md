# 中文部署说明

## 最快预览

项目中的 `dist/` 已经是完整静态站，可直接上传到 Cloudflare Pages、Workers Static Assets、Netlify、Vercel 或普通对象存储。

```bash
python3 -m http.server 8080 --directory dist
```

浏览器打开 `http://localhost:8080`。

## 使用 Astro 正式构建

```bash
corepack enable
corepack prepare pnpm@11.19.0 --activate
pnpm install
cp .env.example .env
pnpm check
pnpm build
```

把 `.env` 中的 `SITE_URL` 改成最终域名，否则 canonical、OG 图片和 sitemap 会继续使用示例域名。

## 部署到 Cloudflare Worker

```bash
pnpm deploy
```

`wrangler.jsonc` 已配置为从 `dist/` 发布静态资源。首次部署前需要执行 `npx wrangler login`，或者在 CI 中配置 Cloudflare API Token。

## 必须更新的运营信息

正式上线前检查以下内容：

1. `SITE_URL` 与最终域名。
2. 博物馆及橹的开放时间、冬季休馆、票价。
3. 北侧停车场施工与可用车位数量。
4. 餐厅营业时间、休息日与停业状态。
5. 樱花与红叶专题不要预写固定“最佳日”，应发布当年开花/色づき更新。

## 图片版权

不要删除 `/credits/` 页面、图片下方的署名，以及 `IMAGE_CREDITS.md`。照片不属于项目MIT代码许可，各自遵循Public Domain、CC0、CC BY或CC BY-SA条款。
