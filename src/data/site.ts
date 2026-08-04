export const site = {
  name: "上田城を歩く",
  englishName: "UEDA CASTLE WALK",
  description: "真田昌幸が築いた上田城を、歴史・地形・建築・城下町の視点から歩くための現地ガイド。",
  address: "長野県上田市二の丸6263番地イ",
  coordinates: { latitude: 36.4035624, longitude: 138.2459171 },
  gaId: import.meta.env.PUBLIC_GA_ID ?? "G-HXM22WWPKP",
  nav: [
    { href: "/history/", label: "歴史" },
    { href: "/highlights/", label: "見どころ" },
    { href: "/routes/", label: "散策ルート" },
    { href: "/access/", label: "アクセス" },
    { href: "/food/", label: "城下町グルメ" },
    { href: "/seasons/", label: "四季" },
  ],
  quickFacts: [
    { label: "上田駅から", value: "徒歩 約12分" },
    { label: "城跡公園", value: "24時間・無料" },
    { label: "おすすめ滞在", value: "60–120分" },
    { label: "城郭タイプ", value: "平城・国史跡" },
  ],
} as const;

export type NavItem = (typeof site.nav)[number];
