export interface RoutePlan {
  id: string;
  minutes: number;
  title: string;
  subtitle: string;
  distance: string;
  steps: string[];
  suitable: string[];
  note: string;
}

export const routes: RoutePlan[] = [
  {
    id: "short",
    minutes: 30,
    title: "代表景観をつなぐ短縮コース",
    subtitle: "時間が限られる人へ",
    distance: "約0.8km",
    steps: ["二の丸橋", "東虎口櫓門", "真田石", "眞田神社", "西櫓"],
    suitable: ["乗換の合間", "初訪問", "外観中心"],
    note: "尼ヶ淵へ下りず、本丸の主要景観に絞ります。",
  },
  {
    id: "standard",
    minutes: 60,
    title: "城の輪郭を読む標準コース",
    subtitle: "初めてなら最もおすすめ",
    distance: "約1.5km",
    steps: ["東虎口櫓門", "南・北櫓", "眞田神社", "真田井戸", "西櫓", "尼ヶ淵", "本丸水堀"],
    suitable: ["歴史と写真", "城郭地形", "散歩"],
    note: "門・櫓・地形を一続きで理解できる基本ルートです。",
  },
  {
    id: "deep",
    minutes: 120,
    title: "建物と歴史を深掘るコース",
    subtitle: "城好き・真田史好きへ",
    distance: "約2.3km",
    steps: ["東虎口櫓門", "南・北櫓内部", "本丸一周", "西櫓", "尼ヶ淵", "上田市立博物館", "ケヤキ並木"],
    suitable: ["博物館", "日本100名城", "雨天にも"],
    note: "博物館と櫓の開館日・最終入館を必ず確認してください。",
  },
];
