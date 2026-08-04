export interface FoodTheme {
  id: string;
  name: string;
  image: string;
  alt: string;
  lead: string;
  howToEnjoy: string;
  area: string;
}

export const foodThemes: FoodTheme[] = [
  {
    id: "oidare",
    name: "美味だれ焼き鳥",
    image: "/images/food-yakitori.webp",
    alt: "炭火で焼かれる焼き鳥のイメージ",
    lead: "すりおろしニンニク入りの醤油だれを、焼きたての串へ。店ごとの味を比べる上田の夜の定番です。",
    howToEnjoy: "夕方以降に営業する店が多いため、上田城の散策後か宿泊日の夜に。写真は日本の焼き鳥調理イメージで、上田の特定店舗ではありません。",
    area: "上田駅・海野町・袋町",
  },
  {
    id: "ankake",
    name: "上田あんかけ焼きそば",
    image: "/images/food-ankake.webp",
    alt: "上田の日昌亭のあんかけ焼きそば",
    lead: "細い麺と野菜あんを、からし酢で食べる上田のソウルフード。",
    howToEnjoy: "昼営業が中心で売り切れや臨時休業もあるため、城へ入る前に当日の営業を確認すると安心です。",
    area: "中央・袋町",
  },
  {
    id: "soba",
    name: "信州そば",
    image: "/images/food-soba.webp",
    alt: "長野県で供される信州そば",
    lead: "上田では量の多い『田舎盛り』や、近隣産のくるみを使ったつけ汁も楽しめます。",
    howToEnjoy: "上田城近くの大手エリアなら散策の前後に組み込みやすく、人気店は昼のピーク前が狙い目です。写真は長野県内の信州そばです。",
    area: "大手・中央・上田駅周辺",
  },
  {
    id: "sweet",
    name: "城下町の甘味・みすゞ飴",
    image: "/images/food-misuzuame.webp",
    alt: "上田名産のみすゞ飴",
    lead: "果物の風味を生かしたみすゞ飴や、焼きたての志゛まんやきは散歩の小休止と土産に。",
    howToEnjoy: "上田城から柳町、海野町、上田駅へ歩く途中に一品だけ立ち寄ると、半日コースに余白が生まれます。",
    area: "海野町・柳町・上田駅前",
  },
];

export const eatingExamples = [
  {
    name: "信州蕎麦の草笛 上田お城前店",
    category: "信州そば",
    walk: "上田城から徒歩約3分",
    hours: "11:00頃から昼営業",
    point: "城のすぐ近く。量の多いそばを選びやすく、移動が少ない。",
    verify: "営業時間・売切れを当日確認",
  },
  {
    name: "日昌亭",
    category: "あんかけ焼きそば",
    walk: "上田城から徒歩約15分",
    hours: "昼中心／水曜休の案内あり",
    point: "上田あんかけ焼きそばを代表する一軒。写真素材も同店の料理。",
    verify: "臨時休業・連休を電話等で確認",
  },
  {
    name: "富士アイス",
    category: "志゛まんやき",
    walk: "上田城から徒歩約10分",
    hours: "9:30–19:00の案内／売切れ次第終了",
    point: "あんことカスタードの焼きたて甘味。城下町散歩の持ち歩きに。",
    verify: "火曜・不定休に注意",
  },
  {
    name: "つづらや",
    category: "美味だれ焼き鳥",
    walk: "上田城から徒歩約12分",
    hours: "17:00–22:00の案内",
    point: "長く続く美味だれ焼き鳥店。夕方以降の城下町コース向き。",
    verify: "日曜・祝日休の案内を当日確認",
  },
] as const;
