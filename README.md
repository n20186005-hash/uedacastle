# 上田城を歩く — UEDA CASTLE WALK

上田城を「門の記念写真だけで終わらせず」、西櫓・尼ヶ淵・土塁・水堀・城下町まで歩いて理解するための、日語単一言語の非公式観光ガイドです。

## 収録内容

- 上田城の歴史と二度の上田合戦
- 現存・再移築・復元・遺構・伝承を区別した12の見どころ
- 30分／60分／120分の散策ルートと半日コース
- 上田駅からの徒歩、自動車、駐車場、段差を減らした動線
- 美味だれ焼き鳥、あんかけ焼きそば、信州そば、柳町の食
- 桜、夏の緑、紅葉、冬の地形観察
- ルート生成、見どころ保存、URL共有、季節切替
- オリジナルSVG城内マップ、FAQ、構造化データ、PWA基礎対応
- 実写写真14点の作者・ライセンス・加工内容を記載したクレジットページ

## 技術構成

- Astro `7.1.6`
- Tailwind CSS `4.3.3`
- TypeScript `6.0.3`
- pnpm `11.19.0`
- Wrangler `4.113.0`
- Cloudflare Workers Static Assets
- データベース、ログイン、CMSなし
- GA4: `G-HXM22WWPKP`

依存関係は `package.json` で完全固定しています。初回インストール時に `pnpm-lock.yaml` が生成されます。

## ローカル開発

```bash
corepack enable
corepack prepare pnpm@11.19.0 --activate
pnpm install
cp .env.example .env
pnpm dev
```

`.env` の `SITE_URL` を公開予定の本番URLへ変更してください。

## 品質確認とビルド

```bash
pnpm check
pnpm build
python3 scripts/validate_dist.py
pnpm preview
```

## Cloudflare Workersへ公開

```bash
pnpm deploy
```

`wrangler.jsonc` は `dist` をStatic Assetsとして配信する設定です。Cloudflare DashboardからGit連携する場合は次を指定します。

- Build command: `pnpm build`
- Deploy command: `npx wrangler deploy`
- Build output: `dist`
- Environment variable: `SITE_URL=https://本番ドメイン`

## 依存関係を入れずに確認する

この納品物には、レビューと緊急公開用の事前生成済み `dist/` も含まれます。`dist` の内容は静的ホスティングへそのままアップロードできます。

```bash
python3 -m http.server 8080 --directory dist
```

`dist` は依存パッケージを取得できない制作環境でも画面を検証できるよう、`scripts/build-static-preview.py` でも再生成できます。正式運用では通常の `pnpm build` を使用してください。

## 写真とライセンス

写真はWikimedia Commons上で再利用条件を確認できる実写素材です。各ページのキャプションと `/credits/`、さらに `IMAGE_CREDITS.md` に作者・ライセンス・原典・加工内容を記載しています。

サイトコードはMIT Licenseです。ただし写真ファイルは各写真の個別ライセンスに従い、MIT Licenseには含まれません。

## 情報更新

歴史・開館・料金・交通・駐車情報は公開後も定期的に再確認してください。参照先は `CONTENT_SOURCES.md` にまとめています。
