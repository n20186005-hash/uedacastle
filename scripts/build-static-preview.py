#!/usr/bin/env python3
"""Build a dependency-free static preview of the Astro project.

This is not a replacement for `pnpm build`; it exists so the complete design
can be reviewed even in environments where the npm registry is unavailable.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PUBLIC = ROOT / "public"
SITE = "https://ueda-castle-walk.example"
GA_ID = "G-HXM22WWPKP"

NAV = [
    ("/history/", "歴史"),
    ("/highlights/", "見どころ"),
    ("/routes/", "散策ルート"),
    ("/access/", "アクセス"),
    ("/food/", "城下町グルメ"),
    ("/seasons/", "四季"),
]

SPOTS = [
    {"id":"east-gate","n":1,"name":"東虎口櫓門","status":"復元","time":"5–10分","fee":"外観無料","image":"/images/hero-spring.webp","alt":"桜に囲まれた上田城東虎口櫓門","summary":"古写真と発掘調査をもとに1994年に復元された、上田城の代表景観。","detail":"南櫓と北櫓をつなぐ本丸東側の入口。門の前で石垣・木部・白壁の重なりを見ると、現在の城址がどの時代の姿を伝えているかが分かります。"},
    {"id":"south-turret","n":2,"name":"南櫓・北櫓","status":"再移築","time":"15–25分","fee":"内部は有料","image":"/images/south-turret.webp","alt":"上田城南櫓","summary":"明治期に城外へ移され、市民の力で買い戻されて城址へ戻った江戸期の櫓。","detail":"建物自体は江戸時代のものですが現在の位置には再移築されています。開館期には内部を見学できます。"},
    {"id":"sanada-stone","n":3,"name":"真田石","status":"伝承","time":"3分","fee":"無料","summary":"東虎口の石垣に組み込まれた巨石。真田信之にまつわる伝承が残ります。","detail":"移封時に持ち出そうとしても動かなかったという話で知られます。史実として断定せず、城下で語り継がれた物語として楽しむ場所です。"},
    {"id":"sanada-shrine","n":4,"name":"眞田神社","status":"施設","time":"10分","fee":"参拝無料","image":"/images/shrine.webp","alt":"上田城内の眞田神社","summary":"真田・仙石・松平の歴代城主を祀る、本丸内の神社。","detail":"『落ちない城』の物語から合格・勝運を願う参拝者にも親しまれています。"},
    {"id":"sanada-well","n":5,"name":"真田井戸","status":"伝承","time":"3分","fee":"無料","summary":"城外へ通じる抜け穴があったと語られる、本丸の井戸。","detail":"秘密通路の存在は確認されていません。籠城時の水源という役割と、後世の伝説を分けて読みます。"},
    {"id":"west-turret","n":6,"name":"西櫓","status":"現存","time":"5–10分","fee":"内部非公開","image":"/images/amagafuchi.webp","alt":"尼ヶ淵から見上げる西櫓","summary":"上田城で唯一、建てられた場所に残り続ける櫓。","detail":"江戸初期の城郭建築で、尼ヶ淵の崖上に立ちます。内部は公開されていません。"},
    {"id":"amagafuchi","n":7,"name":"尼ヶ淵","status":"遺構","time":"10–15分","fee":"無料","image":"/images/amagafuchi.webp","alt":"尼ヶ淵の広場と崖上の櫓","summary":"千曲川の分流と崖を利用した、上田城南側の天然要害。","detail":"現在は広場ですが、かつては水流と断崖が天然の堀をつくりました。下から城を見上げることで難攻不落の理由が立体的に分かります。"},
    {"id":"moat","n":8,"name":"本丸土塁・水堀","status":"遺構","time":"15–20分","fee":"無料","summary":"高い天守ではなく、土・水・地形で守った城の輪郭。","detail":"本丸を一周し、堀の曲がりや高低差を追うと、攻め手の動きを制限する設計が見えてきます。"},
    {"id":"oni-mon","n":9,"name":"隅欠","status":"遺構","time":"5分","fee":"無料","summary":"本丸北東角を内側へ欠いた、鬼門除けとされる縄張り。","detail":"郭の角が切り込まれています。方位観と城の設計が重なる小さな見どころです。"},
    {"id":"keyaki","n":10,"name":"ケヤキ並木遊歩道","status":"遺構","time":"10–15分","fee":"無料","image":"/images/keyaki.webp","alt":"ケヤキ並木遊歩道","summary":"二の丸堀から鉄道、そして緑の遊歩道へ姿を変えた道。","detail":"昭和初期には堀跡を鉄道が通り、廃線後に遊歩道となりました。"},
    {"id":"museum","n":11,"name":"上田市立博物館","status":"施設","time":"35–60分","fee":"有料","image":"/images/museum.webp","alt":"上田市立博物館","summary":"真田・仙石・松平の資料と、上田地域の歴史をつなぐ博物館。","detail":"城を歩くだけでは分かりにくい時代の移り変わりを補えます。"},
    {"id":"ninomaru-bridge","n":12,"name":"二の丸橋","status":"遺構","time":"3分","fee":"無料","image":"/images/entrance.webp","alt":"上田城入口","summary":"駅側から城址へ入るときの起点。旧二の丸堀の輪郭を感じる場所。","detail":"橋の左右に残る高低差を見てから入城すると、かつての堀の広がりを想像しやすくなります。"},
]

ROUTES = [
    {"id":"short","minutes":30,"distance":"約0.8km","title":"代表景観をつなぐ短縮コース","sub":"時間が限られる人へ","steps":["二の丸橋","東虎口櫓門","真田石","眞田神社","西櫓"],"tags":["乗換の合間","初訪問","外観中心"]},
    {"id":"standard","minutes":60,"distance":"約1.5km","title":"城の輪郭を読む標準コース","sub":"初めてなら最もおすすめ","steps":["東虎口櫓門","南・北櫓","眞田神社","真田井戸","西櫓","尼ヶ淵","本丸水堀"],"tags":["歴史と写真","城郭地形","散歩"]},
    {"id":"deep","minutes":120,"distance":"約2.3km","title":"建物と歴史を深掘るコース","sub":"城好き・真田史好きへ","steps":["東虎口櫓門","南・北櫓内部","本丸一周","西櫓","尼ヶ淵","上田市立博物館","ケヤキ並木"],"tags":["博物館","日本100名城","雨天にも"]},
]

FOODS = [
    ("oidare","美味だれ焼き鳥","/images/food-yakitori.webp","すりおろしニンニク入りの醤油だれを焼きたての串へ。店ごとの味を比べる上田の夜の定番。","上田駅・海野町・袋町"),
    ("ankake","上田あんかけ焼きそば","/images/food-ankake.webp","細い麺と野菜あんを、からし酢で食べる上田のソウルフード。","中央・袋町"),
    ("soba","信州そば","/images/food-soba.webp","量の多い田舎盛りや、近隣産のくるみを使ったつけ汁も楽しめます。","大手・中央・駅周辺"),
    ("sweet","城下町の甘味・みすゞ飴","/images/food-misuzuame.webp","みすゞ飴や焼きたての志゛まんやきは散歩の小休止と土産に。","海野町・柳町・駅前"),
]

CREDITS = [
    ("spring","/images/hero-spring.webp","上田城（春）","Hiroaki Kaneko","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/","https://commons.wikimedia.org/wiki/File:%E4%B8%8A%E7%94%B0%E5%9F%8E_(Ueda_Castle_in_spring)_15_Apr,_2013_-_panoramio.jpg"),
    ("entrance","/images/entrance.webp","上田城入口","Abasaa / あばさー","Public Domain","https://creativecommons.org/publicdomain/mark/1.0/","https://commons.wikimedia.org/wiki/File:Entrance_to_Ueda_Castle.JPG"),
    ("amagafuchi","/images/amagafuchi.webp","上田城 尼ヶ淵","Qurren","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/","https://commons.wikimedia.org/wiki/File:Ueda_Castle_Amagafuchi.jpg"),
    ("south-turret","/images/south-turret.webp","上田城 南櫓","Suikotei","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/","https://commons.wikimedia.org/wiki/File:Ueda_Castle_South_Turret.jpg"),
    ("keyaki","/images/keyaki.webp","上田城跡公園ケヤキ並木遊歩道","BehBeh","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/","https://commons.wikimedia.org/wiki/File:20080624%E4%B8%8A%E7%94%B0%E5%9F%8E%E8%B7%A1%E5%85%AC%E5%9C%92%E3%82%B1%E3%83%A4%E3%82%AD%E4%B8%A6%E6%9C%A8%E9%81%8A%E6%AD%A9%E9%81%93.jpg"),
    ("yanagimachi","/images/yanagimachi.webp","柳町（上田市）","Suikotei","CC BY 4.0","https://creativecommons.org/licenses/by/4.0/","https://commons.wikimedia.org/wiki/File:Yanagimachi_(Ueda,_Nagano)_20251130.jpg"),
    ("shrine","/images/shrine.webp","上田城内の眞田神社","Yamaguchi Yoshiaki","CC BY-SA 2.0","https://creativecommons.org/licenses/by-sa/2.0/","https://commons.wikimedia.org/wiki/File:Sanada_shrine_in_Ueda_Castle_(2020392704).jpg"),
    ("museum","/images/museum.webp","上田市立博物館","Qurren","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/","https://commons.wikimedia.org/wiki/File:Ueda_City_Museum_2022-12.jpg"),
    ("autumn","/images/autumn.webp","上田城跡公園の紅葉","Yuya Sekiguchi","CC BY 2.0","https://creativecommons.org/licenses/by/2.0/","https://commons.wikimedia.org/wiki/File:%E3%82%82%E3%81%BF%E3%81%98%E3%81%AE%E7%B4%85%E8%91%89_Autumn_Maple_Leaves_(8316665157).jpg"),
    ("station","/images/station.webp","上田駅 お城口","Mister0124","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/","https://commons.wikimedia.org/wiki/File:JR_East%E3%83%BBShinano_Railway%E3%83%BBUedadentetsu_Ueda_Station_Oshiro_Exit.jpg"),
    ("yakitori","/images/food-yakitori.webp","焼き鳥調理（イメージ）","Yoshiko Kikuraku","CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/","https://commons.wikimedia.org/wiki/File:BEST_YAKITORI_in_local_Japan.jpg"),
    ("ankake","/images/food-ankake.webp","上田あんかけ焼きそば（日昌亭）","Yoit","CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/","https://commons.wikimedia.org/wiki/File:%E4%B8%8A%E7%94%B0%E3%81%82%E3%82%93%E3%81%8B%E3%81%91%E7%84%BC%E3%81%8D%E3%81%9D%E3%81%B0.jpg"),
    ("soba","/images/food-soba.webp","信州そば（長野県内）","663highland","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/","https://commons.wikimedia.org/wiki/File:160429_Shinshu_soba_Nagano_Japan01s8.jpg"),
    ("misuzuame","/images/food-misuzuame.webp","みすゞ飴（上田）","NY066","CC BY-SA 3.0","https://creativecommons.org/licenses/by-sa/3.0/","https://commons.wikimedia.org/wiki/File:Misuzuame@Ueda.JPG"),
]


def mark_svg() -> str:
    return '''<svg class="brand-mark" viewBox="0 0 72 72" aria-hidden="true"><rect width="72" height="72" rx="18" fill="currentColor"/><g fill="#f3ebdd"><path d="M13 36h46v4H13zM18 33l9-10h18l9 10H18zM26 19h20v4H26z"/></g><g fill="#a52a2f"><circle cx="25" cy="50" r="3.4"/><circle cx="36" cy="50" r="3.4"/><circle cx="47" cy="50" r="3.4"/><circle cx="25" cy="59" r="3.4"/><circle cx="36" cy="59" r="3.4"/><circle cx="47" cy="59" r="3.4"/></g></svg>'''


def header(path: str) -> str:
    links = "".join(f'<li><a href="{href}"{(" aria-current=\"page\"" if path.startswith(href) else "")}>{label}</a></li>' for href, label in NAV)
    return f'''<header class="site-header"><div class="container header-inner"><a class="brand" href="/" aria-label="上田城を歩く ホーム">{mark_svg()}<span class="brand-copy"><strong>上田城を歩く</strong><span>UEDA CASTLE WALK</span></span></a><nav class="site-nav" aria-label="主要ナビゲーション" data-menu><ul class="nav-list">{links}</ul></nav><a class="header-cta" href="/routes/#planner">ルートをつくる →</a><button class="menu-button" type="button" aria-label="メニューを開く" aria-expanded="false" data-menu-button><span></span></button></div></header>'''


def footer() -> str:
    links1 = "".join(f'<li><a href="{h}">{l}</a></li>' for h,l in NAV[:4])
    return f'''<footer class="site-footer"><div class="container"><div class="footer-grid"><div class="footer-brand"><a class="brand" href="/">{mark_svg()}<span class="brand-copy"><strong>上田城を歩く</strong><span>UEDA CASTLE WALK</span></span></a><p>天守の大きさではなく、地形・櫓・土塁・城下町の物語から上田城を読み解く、非公式の旅行ガイドです。</p></div><div><h2 class="footer-title">城を歩く</h2><ul class="footer-links">{links1}<li><a href="/faq/">よくある質問</a></li></ul></div><div><h2 class="footer-title">旅を整える</h2><ul class="footer-links"><li><a href="/food/">城下町グルメ</a></li><li><a href="/seasons/">四季の上田城</a></li><li><a href="/credits/">写真・資料について</a></li><li><a href="/sitemap.xml">サイトマップ</a></li></ul></div></div><div class="footer-bottom"><span>© 上田城を歩く. Unofficial travel guide.</span><span>営業・交通情報は出発前に公式発表をご確認ください。</span></div></div></footer>'''


def layout(path: str, title: str, desc: str, body: str, schema: dict | list | None = None, noindex: bool = False) -> str:
    full_title = title if title == "上田城を歩く" else f"{title}｜上田城を歩く"
    canonical = SITE + path
    if not canonical.endswith("/") and path != "/404.html": canonical += "/"
    schema_data = schema or {"@context":"https://schema.org","@type":"WebSite","name":"上田城を歩く","url":SITE+"/","inLanguage":"ja"}
    robots = '<meta name="robots" content="noindex,follow">' if noindex else ""
    return f'''<!doctype html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#191815"><meta name="description" content="{escape(desc)}">{robots}<link rel="canonical" href="{canonical}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="manifest" href="/site.webmanifest"><meta property="og:type" content="website"><meta property="og:locale" content="ja_JP"><meta property="og:site_name" content="上田城を歩く"><meta property="og:title" content="{escape(full_title)}"><meta property="og:description" content="{escape(desc)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{SITE}/images/hero-spring.webp"><meta name="twitter:card" content="summary_large_image"><title>{escape(full_title)}</title><link rel="stylesheet" href="/assets/site.css"><script type="application/ld+json">{json.dumps(schema_data, ensure_ascii=False)}</script><script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{GA_ID}',{{anonymize_ip:true}});</script><script src="/assets/site.js" defer></script></head><body><a class="skip-link" href="#main">本文へ移動</a>{header(path)}<main id="main">{body}</main>{footer()}</body></html>'''


def page_hero(eyebrow: str, title: str, desc: str) -> str:
    return f'''<section class="page-hero"><div class="container"><nav class="breadcrumbs"><a href="/">ホーム</a><span aria-current="page">{escape(title)}</span></nav><span class="eyebrow">{escape(eyebrow)}</span><h1 class="display-title">{escape(title)}</h1><p>{escape(desc)}</p></div></section>'''


def section_heading(eyebrow: str, title: str, desc: str = "") -> str:
    return f'''<header data-reveal><span class="eyebrow">{escape(eyebrow)}</span><h2 class="section-title">{escape(title)}</h2>{f'<p class="section-lede">{escape(desc)}</p>' if desc else ''}</header>'''


def photo(src: str, alt: str, cid: str, credit: str, eager: bool = False) -> str:
    return f'''<figure class="photo-frame"><img src="{src}" alt="{escape(alt)}" loading="{'eager' if eager else 'lazy'}" decoding="async"><figcaption>Photo: <a href="/credits/#{cid}">{escape(credit)}</a></figcaption></figure>'''


def route_cards() -> str:
    out = []
    for r in ROUTES:
        lis = "".join(f"<li>{escape(t)}</li>" for t in r["tags"])
        out.append(f'''<article class="route-card" id="{r['id']}" data-reveal><div class="route-time"><strong>{r['minutes']}</strong><span>MINUTES<br>{r['distance']}</span></div><div class="route-body"><span class="small muted">{r['sub']}</span><h3>{r['title']}</h3><p class="route-path">{' → '.join(r['steps'])}</p><ul class="route-points">{lis}</ul><a class="btn btn-outline btn-sm" href="/routes/#{r['id']}">ルート詳細</a></div></article>''')
    return '<div class="route-cards">'+"".join(out)+"</div>"


def planner() -> str:
    return '''<form class="planner" data-route-planner id="planner"><div class="planner-grid"><div><span class="eyebrow">Route builder</span><h2 class="section-title">あなたの上田城ルート</h2><fieldset class="fieldset"><legend>使える時間</legend><div class="choice-row"><label class="choice"><input type="radio" name="time" value="30"><span>30分</span></label><label class="choice"><input type="radio" name="time" value="60" checked><span>60分</span></label><label class="choice"><input type="radio" name="time" value="120"><span>120分</span></label></div></fieldset><fieldset class="fieldset"><legend>組み込みたいこと</legend><label class="check-choice"><input type="checkbox" name="museum">博物館・櫓の内部も見たい</label><label class="check-choice"><input type="checkbox" name="gentle">階段と急な坂をできるだけ避けたい</label></fieldset><fieldset class="fieldset"><legend>散策後の寄り道</legend><div class="choice-row"><label class="choice"><input type="radio" name="food" value="none" checked><span>寄り道なし</span></label><label class="choice"><input type="radio" name="food" value="soba"><span>信州そば</span></label><label class="choice"><input type="radio" name="food" value="yanagimachi"><span>柳町</span></label></div></fieldset><button class="btn btn-primary" type="submit">ルートをつくる</button></div><div class="planner-result" data-route-result><span class="tag" style="border-color:rgba(255,255,255,.25)">おすすめ</span><h3 data-route-title>60分・城の輪郭を読む標準コース</h3><p class="route-output" data-route-path>二の丸橋 → 東虎口櫓門 → 真田石 → 眞田神社 → 真田井戸 → 西櫓 → 尼ヶ淵</p><p data-route-note>初めての上田城に。櫓門だけでなく、城を守った地形まで歩きます。</p><div class="planner-actions"><button class="btn btn-light btn-sm" type="button" data-share-route>このルートを共有</button><a class="btn btn-ghost btn-sm" href="/access/">アクセスを見る</a></div></div></div></form>'''


def checklist() -> str:
    checks = "".join(f'''<label class="spot-check"><input type="checkbox" data-spot-id="{s['id']}"><span><strong>{s['n']}. {s['name']}</strong><small>{s['time']}・{s['status']}</small></span></label>''' for s in SPOTS)
    return f'''<div class="checklist" data-spot-checklist><div class="checklist-head"><div><strong>歩きたい場所を保存</strong><div class="small muted">端末内に保存し、URLで共有できます。</div></div><div class="check-count"><strong data-check-count>0</strong><span>か所</span></div></div><div class="check-grid">{checks}</div><div class="checklist-actions"><button class="btn btn-primary btn-sm" type="button" data-share-spots>リストを共有</button><button class="btn btn-outline btn-sm" type="button" data-reset-spots>すべて外す</button></div></div>'''


def castle_map() -> str:
    map_ids = ["east-gate","south-turret","sanada-shrine","sanada-well","west-turret","amagafuchi","keyaki","museum"]
    coords = {"east-gate":(500,250),"south-turret":(540,300),"sanada-shrine":(380,245),"sanada-well":(315,205),"west-turret":(208,342),"amagafuchi":(310,450),"keyaki":(585,135),"museum":(615,235)}
    pins=[]; cards=[]
    subset=[s for s in SPOTS if s['id'] in map_ids]
    for i,s in enumerate(subset):
        x,y=coords[s['id']]
        pins.append(f'''<g class="map-pin" transform="translate({x} {y})" data-map-pin="{s['id']}" role="button" tabindex="0" aria-label="{s['n']}. {s['name']}" aria-pressed="{'true' if i==0 else 'false'}"><circle r="14"/><text text-anchor="middle" dominant-baseline="central">{s['n']}</text></g>''')
        cards.append(f'''<div data-map-card="{s['id']}"{' hidden' if i else ''}><span class="tag tag-red">{s['status']}</span><h3>{s['name']}</h3><p>{s['summary']}</p><div class="map-facts"><div class="map-fact"><span>目安</span><strong>{s['time']}</strong></div><div class="map-fact"><span>料金</span><strong>{s['fee']}</strong></div></div><a class="btn btn-outline btn-sm" href="/highlights/#{s['id']}">詳しく読む</a></div>''')
    return f'''<div class="map-shell" data-reveal><div class="castle-map"><svg viewBox="0 0 760 570" role="img" aria-label="上田城跡公園の見どころ概略図"><path class="map-water" d="M0 475 C160 430 230 505 390 460 C540 418 625 465 760 425 L760 570 L0 570 Z"/><path class="map-land" d="M118 85 L635 72 L690 175 L661 365 L535 418 L168 405 L91 305 Z"/><path class="map-moat" d="M210 145 C300 90 505 98 562 150 C615 198 608 315 548 350 C468 396 270 394 194 335 C142 295 144 194 210 145 Z"/><path class="map-wall" d="M246 165 L490 148 L545 204 L526 318 L433 356 L252 333 L195 280 L207 205 Z"/><path class="map-path" d="M675 180 C625 190 602 214 572 242 C530 280 504 320 450 370"/><path class="map-path" d="M615 78 L615 367"/><rect class="map-wood" x="477" y="231" width="38" height="33" rx="3"/><rect class="map-wood" x="501" y="280" width="31" height="34" rx="3"/><rect class="map-wood" x="182" y="320" width="35" height="32" rx="3"/><rect class="map-green" x="315" y="198" width="105" height="70" rx="16"/><rect class="map-green" x="575" y="90" width="48" height="280" rx="20"/><rect x="593" y="207" width="74" height="52" rx="5" fill="#b5ab9a"/><text class="map-label" x="315" y="180">本丸</text><text class="map-label" x="603" y="118" transform="rotate(90 603 118)">ケヤキ並木遊歩道</text><text class="map-label" x="276" y="514">尼ヶ淵・旧千曲川分流</text><text class="map-label" x="590" y="282">二の丸</text>{''.join(pins)}</svg></div><aside class="map-panel" aria-live="polite">{''.join(cards)}</aside></div>'''


def season_switcher() -> str:
    panels = [
        ("spring",False,"/images/hero-spring.webp","桜が咲く上田城東虎口櫓門","spring","Hiroaki Kaneko / CC BY-SA 3.0","Spring","門と桜が重なる、最も華やかな季節","東虎口櫓門の枝垂れ桜、本丸の堀沿い、尼ヶ淵の眺めが主役。開花は年により動くため、直前情報で判断します。",["朝は門前の人が少なく建物を撮りやすい","催事期間は駐車料金・交通規制が通常期と異なる","夜間ライトアップ時も足元に注意"]),
        ("summer",True,"/images/keyaki.webp","夏のケヤキ並木遊歩道","keyaki","BehBeh / CC BY-SA 3.0","Summer","深い緑の中で、堀跡を歩く","夏はケヤキ並木と水堀の緑が中心。朝に城内、昼に博物館という順序が歩きやすい構成です。",["木陰の多いケヤキ並木を休憩に使う","尼ヶ淵は日差しを遮る場所が少ない","博物館を暑い時間帯へ組み込む"]),
        ("autumn",True,"/images/autumn.webp","上田城跡公園の紅葉","autumn","Yuya Sekiguchi / CC BY 2.0","Autumn","紅葉と石垣が最も深く見える季節","ケヤキ並木、本丸護城河、尼ヶ淵をつなぐと、黄・赤・城郭建築の表情を一度に楽しめます。",["朝夕は葉の透過光を狙う","11月中旬以降は櫓の冬季休館に注意","紅葉祭など催事日は混雑を見込む"]),
        ("winter",True,"/images/amagafuchi.webp","冬の尼ヶ淵と西櫓","amagafuchi","Qurren / CC BY-SA 3.0","Winter","葉が落ちて、城の骨格が見える","華やかさより土塁・堀・崖の輪郭を読む季節。櫓内部は例年冬季休館です。",["凍結時は尼ヶ淵への階段を避ける","落葉後は西櫓と土塁が見通しやすい","日没が早いため時間に余裕を持つ"]),
    ]
    tabs=''.join(f'''<button class="season-tab" type="button" role="tab" aria-selected="{'true' if i==0 else 'false'}" data-season="{p[0]}">{['春','夏','秋','冬'][i]}</button>''' for i,p in enumerate(panels))
    html=[]
    for key,hidden,src,alt,cid,cred,eye,title,desc,lis in panels:
        html.append(f'''<div class="season-panel" data-season-panel="{key}"{' hidden' if hidden else ''}>{photo(src,alt,cid,cred)}<div><span class="eyebrow">{eye}</span><h3 class="section-title">{title}</h3><p>{desc}</p><ul class="season-list">{''.join(f'<li>{x}</li>' for x in lis)}</ul>{'<a class="btn btn-light btn-sm" href="/sakura/">桜の歩き方</a>' if key=='spring' else '<a class="btn btn-light btn-sm" href="/autumn/">紅葉の歩き方</a>' if key=='autumn' else ''}</div></div>''')
    return f'''<div data-season-switcher><div class="season-tabs" role="tablist" aria-label="季節を選ぶ">{tabs}</div>{''.join(html)}</div>'''


def cta(title: str, text: str, href: str, label: str) -> str:
    return f'''<div class="cta-banner" data-reveal><div><h2>{escape(title)}</h2><p>{escape(text)}</p></div><a class="btn btn-light" href="{href}">{escape(label)} →</a></div>'''


def home() -> str:
    quick = [("上田駅から","徒歩 約12分"),("城跡公園","24時間・無料"),("おすすめ滞在","60–120分"),("城郭タイプ","平城・国史跡")]
    qgrid=''.join(f'<div class="quick-item"><span class="quick-label">{a}</span><strong class="quick-value">{b}</strong></div>' for a,b in quick)
    facts=''.join(f'<div><dt>{a}</dt><dd>{b}</dd></div>' for a,b in quick)
    timeline=[("1583","真田昌幸が築城を開始","上田盆地と千曲川を見渡す地に、実戦的な城と城下町を整えます。"),("1585","第一次上田合戦","約7,000の徳川軍に対し、2,000に満たない真田方が城下を使って抵抗しました。"),("1600","第二次上田合戦","徳川秀忠の大軍を上田で足止めし、進軍を遅らせます。"),("1601","破城","関ヶ原後、真田昌幸・信繁は九度山へ。上田城は破壊されました。"),("1626","仙石忠政が復興","現在の城郭建築へつながる復興が始まります。"),("1949","南櫓・北櫓が城址へ戻る","市民が買い戻し、再び城址へ移築しました。"),("1994","東虎口櫓門を復元","古写真と発掘調査をもとに代表景観がよみがえりました。")]
    t_html=''.join(f'<article class="timeline-item" data-reveal><div class="timeline-year">{y}</div><span class="timeline-dot"></span><div class="timeline-body"><h3>{t}</h3><p>{d}</p></div></article>' for y,t,d in timeline)
    food_html=''.join(f'''<article class="food-card" data-reveal><img src="{img}" alt="{name}" loading="lazy"><div class="food-card-body"><span class="tag" style="border-color:rgba(255,255,255,.28)">{area}</span><h3>{name}</h3><p>{desc}</p></div></article>''' for _,name,img,desc,area in FOODS)
    faq_html=''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in [
        ("上田城に天守はありますか？","現在、見学できる天守はありません。櫓、櫓門、石垣、土塁、堀、尼ヶ淵が主な見どころです。"),
        ("上田城跡公園は無料ですか？","公園は24時間入園でき無料です。博物館と南・北櫓の内部は有料です。"),
        ("見学時間はどのくらい必要ですか？","代表景観なら30分、地形まで60分、博物館と内部見学なら約120分です。"),
        ("車椅子やベビーカーで歩けますか？","北側から本丸へは比較的穏やかです。尼ヶ淵への階段は避けるルートを選べます。"),
        ("雨の日でも楽しめますか？","博物館と南・北櫓を中心にできますが、休館日と最終入館を先に確認してください。")])
    return f'''<section class="hero"><div class="container hero-grid"><div><span class="hero-kicker">Sanada’s fortified town · Shinshu</span><h1 class="display-title"><small>二度、徳川の大軍を退けた真田の城</small>天守はなくても、<br>物語は残っている。</h1><p class="hero-lede">門を撮って終わらない。西櫓、尼ヶ淵、土塁、水堀を歩きながら、上田城がなぜ「難攻不落」と呼ばれたのかを一時間で読み解きます。</p><div class="hero-actions"><a class="btn btn-primary" href="#map">見どころを地図で見る ↓</a><a class="btn btn-light" href="#planner">散策ルートをつくる →</a></div></div><aside class="hero-panel"><dl>{facts}</dl><p class="photo-note">Photo: Hiroaki Kaneko / CC BY-SA 3.0</p></aside></div></section><div class="quick-strip"><div class="container quick-grid">{qgrid}</div></div>
<section class="section"><div class="container">{section_heading('Why Ueda Castle','天守がない上田城で、何を見る？','上田城の価値は、巨大な建物ではなく、戦い・地形・保存の時間が同じ場所で読めることにあります。')}<div class="grid-3" style="margin-top:2.5rem"><article class="reason-card" data-reveal><div class="number">01</div><h3>二度の上田合戦</h3><p>1585年と1600年、真田昌幸は徳川軍の進撃を阻みました。城下町と地形を含む防御の物語です。</p><a href="/history/">合戦の流れを読む →</a></article><article class="reason-card" data-reveal><div class="number">02</div><h3>天然要害の地形</h3><p>千曲川の分流、尼ヶ淵の崖、土塁、水堀。下から見上げると、強さが建物の高さではなかったと分かります。</p><a href="/highlights/#amagafuchi">尼ヶ淵を見る →</a></article><article class="reason-card" data-reveal><div class="number">03</div><h3>現存・再移築・復元</h3><p>西櫓は原位置に現存、南北櫓は買い戻して再移築、櫓門は資料をもとに復元。</p><a href="#authenticity">建物の違いを知る →</a></article></div></div></section>
<section class="section section-paper"><div class="container split">{photo('/images/amagafuchi.webp','尼ヶ淵から見上げる上田城','amagafuchi','Qurren / CC BY-SA 3.0')}<div data-reveal><span class="eyebrow">Read the terrain</span><h2 class="section-title">「難攻不落」は、崖の下から見えてくる。</h2><p>現在の尼ヶ淵は静かな広場ですが、かつて南側には千曲川の分流が流れ、急な崖と一体になって天然の堀をつくりました。</p><p>西櫓から尼ヶ淵へ下りて振り返る。それだけで、平面の城跡が立体的な防御施設として見え始めます。</p><a class="btn btn-ink" href="/highlights/">城内12の見どころ</a></div></div></section>
<section class="section section-dark"><div class="container">{section_heading('Four centuries','1583年から今へ。城が壊され、戻ってきた時間。','今日の上田城は、真田時代そのままの姿ではありません。破城、復興、廃城、再移築、復元という時間の層を歩く場所です。')}<div class="timeline">{t_html}</div><p><a class="btn btn-light" href="/history/">上田城の歴史を詳しく読む</a></p></div></section>
<section class="section" id="authenticity"><div class="container">{section_heading('What is original?','目の前の建物は、いつの上田城か。','「本物か復元か」を一括りにせず、それぞれの保存の経緯を知ることが上田城の面白さです。')}<div class="authenticity"><article class="authenticity-card"><div class="authenticity-label existing">現存</div><h3>西櫓</h3><p>江戸初期に建てられた場所に残り続ける、上田城唯一の原位置現存櫓。</p></article><article class="authenticity-card"><div class="authenticity-label returned">再移築</div><h3>南櫓・北櫓</h3><p>城外へ移築された江戸期の建物を買い戻し、1949年に城址へ戻しました。</p></article><article class="authenticity-card"><div class="authenticity-label restored">復元</div><h3>東虎口櫓門</h3><p>古写真、発掘調査、建築資料をもとに1994年に復元。</p></article></div></div></section>
<section class="section section-paper" id="map"><div class="container">{section_heading('Interactive map','城内地図から、物語の場所を選ぶ。','建物だけでなく、堀跡・崖・遊歩道まで含めて位置関係をつかむオリジナル概略図です。')}{castle_map()}</div></section>
<section class="section"><div class="container">{section_heading('Choose your pace','30分、60分、120分。時間で選ぶ散策。','内部見学を加える場合だけ、博物館と櫓の開館時間を起点に組み立てます。')}{route_cards()}</div></section>
<section class="section section-dark"><div class="container">{planner()}</div></section>
<section class="section section-dark" style="padding-top:0"><div class="container">{section_heading('Four seasons','同じ城でも、歩く理由は季節で変わる。','桜だけでなく、新緑、紅葉、落葉後の地形まで。')}{season_switcher()}</div></section>
<section class="section"><div class="container">{section_heading('Access','上田駅から歩いて12分。城下町ごと旅にする。','入口・道順・駐車場の高低差まで把握しておくと現地で迷いません。')}<div class="access-cards" style="margin-top:2rem"><article class="access-card"><div class="access-icon">歩</div><h3>上田駅から徒歩</h3><div class="big">約12分</div><p>「お城口」から二の丸橋へ。</p></article><article class="access-card"><div class="access-icon">車</div><h3>上田菅平ICから</h3><div class="big">約15分・4km</div><p>北側は高低差が少なく、南側は尼ヶ淵に近い。</p></article><article class="access-card"><div class="access-icon">新</div><h3>東京から新幹線</h3><div class="big">約90分</div><p>北陸新幹線で日帰り圏。</p></article></div><div class="notice" style="margin-top:1.4rem"><span class="notice-icon">注</span><p>北側駐車場は工事・催事などにより利用可能台数が変わる場合があります。出発前に公式発表をご確認ください。</p></div><p style="margin-top:1.4rem"><a class="btn btn-ink" href="/access/">徒歩ルート・駐車場を確認</a></p></div></section>
<section class="section section-paper"><div class="container">{section_heading('Castle-town table','城を出たら、上田の味へ。','昼は信州そばとあんかけ焼きそば、散歩には甘味、夜は美味だれ焼き鳥。')}<div class="food-grid" style="margin-top:2.2rem">{food_html}</div><p class="small muted">※焼き鳥・信州そばの写真は料理イメージを含みます。撮影地とライセンスは写真クレジットに明記。</p><p><a class="btn btn-ink" href="/food/">近くの店と食べ方を見る</a></p></div></section>
<section class="section"><div class="container split reverse">{photo('/images/yanagimachi.webp','上田市柳町','yanagimachi','Suikotei / CC BY 4.0')}<div data-reveal><span class="eyebrow">Half-day walk</span><h2 class="section-title">上田城から柳町へ。発酵の町を歩く半日。</h2><p>上田城から柳町までは徒歩約10分。旧北国街道の町家に、酒、味噌、パン、そば、甘味が集まります。</p><p><strong>上田駅 → 上田城 → 博物館 → 柳町 → 海野町 → 上田駅</strong></p><a class="btn btn-ink" href="/routes/#half-day">半日コースを見る</a></div></div></section>
<section class="section section-paper"><div class="container">{section_heading('Save your places','歩きたい場所だけ、自分のリストへ。','現地で見る場所を選び、同じ端末に保存できます。')}{checklist()}</div></section>
<section class="section"><div class="narrow">{section_heading('FAQ','出発前に知っておきたいこと。')}<div class="faq" style="margin-top:2rem">{faq_html}</div><p style="margin-top:1.5rem"><a class="btn btn-outline" href="/faq/">すべての質問を見る</a></p></div></section>
<section class="section section-sm"><div class="container">{cta('最初の一時間を、門前だけで終わらせない。','時間・博物館・食事の希望から、自分向けの上田城ルートを作れます。','/routes/#planner','散策ルートをつくる')}</div></section>'''


def history_page() -> str:
    return page_hero("History","上田城の歴史","真田の城として始まり、壊され、別の城主により復興され、市民の手で建物が戻った。現在の景色をつくった四百年をたどります。") + '''<section class="section"><article class="narrow prose"><p class="lead">上田城の歴史は、真田氏だけで完結しません。1583年の築城、二度の戦い、関ヶ原後の破城、仙石氏による復興、松平氏の時代、明治の廃城、そして市民による櫓の買い戻しまでが、今の城址を形づくっています。</p><div class="fact-box"><strong>現地で見る視点</strong><p>真田時代の完全な城ではなく、各時代の痕跡が重なる場所として歩きます。</p></div><h2>1583年、真田昌幸が城を築く</h2><p>上田盆地の中央、千曲川北岸の河岸段丘に築城。南側の尼ヶ淵は川の分流と断崖を利用できる位置でした。</p><h2>1585年、第一次上田合戦</h2><p>公式解説では徳川方約7,000、真田方2,000未満。真田方は城下へ敵を引き込み、狭い道と伏兵を使って反撃しました。</p><div class="quote-panel"><blockquote>「城壁の高さ」ではなく、敵の隊列を崩す地形と町の構造が武器だった。</blockquote><cite>現地を歩くための要約</cite></div><h2>1600年、第二次上田合戦</h2><p>徳川秀忠の約38,000の軍勢は上田で進軍を遅らせます。交渉・攻防・行軍判断が重なった出来事として読みます。</p><h2>1601年、破城</h2><p>昌幸と信繁は九度山へ配流され、上田城は破壊されました。現在の主要な櫓が真田時代の建物ではない理由です。</p><h2>1626年、仙石忠政が復興</h2><p>幕府の許可を得て復興を始めますが、1628年の死去で未完成のまま止まります。1706年以降は松平氏が治めました。</p><h2>1874年以降、廃城から保存へ</h2><p>南櫓・北櫓は城外へ移されましたが、市民が買い戻して1949年に再移築。東虎口櫓門は1994年に復元されました。</p></article></section>''' + f'''<section class="section section-paper"><div class="container split">{photo('/images/south-turret.webp','上田城南櫓','south-turret','Suikotei / CC BY-SA 4.0')}<div><span class="eyebrow">Three ways of survival</span><h2 class="section-title">残った、戻った、復元された。</h2><p><strong>西櫓：</strong>原位置に現存。<br><strong>南櫓・北櫓：</strong>城外から再移築。<br><strong>東虎口櫓門：</strong>資料をもとに復元。</p><a class="btn btn-ink" href="/highlights/">現地の見どころへ</a></div></div></section><section class="section section-sm"><div class="container">{cta('歴史を、現地の順番で歩く。','門・本丸・西櫓・尼ヶ淵をつなぐ60分ルートへ。','/routes/#standard','標準ルートを見る')}</div></section>'''


def highlights_page() -> str:
    rows=[]
    for s in SPOTS:
        img=f'<img src="{s["image"]}" alt="{s["alt"]}" loading="lazy">' if s.get('image') else f'<div style="min-height:225px;background:linear-gradient(135deg,#d8cfbe,#a8a194);display:grid;place-items:center;font-family:var(--serif);font-size:3rem;color:rgba(25,24,21,.28)">{s["n"]:02d}</div>'
        rows.append(f'''<article class="spot-row" id="{s['id']}" data-reveal>{img}<div class="spot-row-body"><div class="spot-row-head"><div><span class="card-index">{s['n']:02d}</span><h2>{s['name']}</h2></div><span class="tag tag-red">{s['status']}</span></div><p><strong>{s['summary']}</strong></p><p>{s['detail']}</p><div class="card-meta"><span class="tag">目安 {s['time']}</span><span class="tag">{s['fee']}</span></div></div></article>''')
    return page_hero("Highlights","城内12の見どころ","建物だけでなく、崖・堀・土塁・近代鉄道の跡まで。『何を見るか』と同時に『なぜ見るか』をまとめました。") + f'''<section class="section section-paper"><div class="container">{castle_map()}</div></section><section class="section"><div class="container"><div class="legend-box" style="margin-bottom:2rem"><strong>表示の見方：</strong>現存・再移築・復元・伝承を分けて紹介しています。</div><div class="spot-list">{''.join(rows)}</div></div></section><section class="section section-sm"><div class="container">{cta('全部を見る必要はありません。','使える時間と体力に合わせて見どころをつなぎます。','/routes/','散策ルートを選ぶ')}</div></section>'''


def routes_page() -> str:
    return page_hero("Routes","散策ルート","時間だけでなく、博物館、段差、写真、食事まで含めて選ぶ。門前で終わらせないための歩き方です。") + f'''<section class="section"><div class="container">{route_cards()}</div></section><section class="section section-dark"><div class="container">{planner()}</div></section><section class="section section-paper" id="half-day"><div class="container split reverse">{photo('/images/yanagimachi.webp','柳町','yanagimachi','Suikotei / CC BY 4.0')}<div><span class="eyebrow">Half-day · 4 hours</span><h2 class="section-title">上田城と柳町、城下町半日コース</h2><p><strong>上田駅 → 上田城 → 上田市立博物館 → 柳町 → 海野町 → 上田駅</strong></p><p>城内を約90分歩き、徒歩約10分で柳町へ。発酵文化、そば、甘味を組み合わせます。</p><ul><li>午前：上田城の外観と尼ヶ淵</li><li>11時台：博物館または櫓内部</li><li>昼：大手・柳町で信州そば</li><li>午後：柳町と海野町を経て駅へ</li></ul></div></div></section><section class="section"><div class="container grid-2"><article class="card"><div class="card-body"><span class="tag tag-moss">段差を減らす</span><h2>北側から本丸へ</h2><p>尼ヶ淵への階段を使わず、東虎口櫓門、本丸、眞田神社、西櫓外観へ。</p></div></article><article class="card"><div class="card-body"><span class="tag tag-red">Photography</span><h2>朝と夕方の写真ルート</h2><p>朝は櫓門と水堀、午後は南櫓、夕方は尼ヶ淵から西櫓。</p></div></article></div></section><section class="section section-paper"><div class="container"><h2 class="section-title">自分の見どころリスト</h2>{checklist()}</div></section>'''


def access_page() -> str:
    return page_hero("Access","アクセス・駐車場","上田駅から徒歩約12分。車なら、駐車場の近さより『どこへ出るか』『高低差があるか』で選びます。") + f'''<section class="section"><div class="container split">{photo('/images/station.webp','上田駅お城口','station','Mister0124 / CC BY-SA 4.0')}<div><span class="eyebrow">From Ueda Station</span><h2 class="section-title">「お城口」から徒歩約12分。</h2><ol><li>上田駅のお城口へ出る。</li><li>松尾町・中央方面へ北上。</li><li>市役所・観光会館方面へ。</li><li>二の丸橋から公園へ入る。</li></ol><div class="hero-actions"><a class="btn btn-primary" href="https://www.google.com/maps/search/?api=1&query=36.4035624,138.2459171" target="_blank" rel="noreferrer">Google マップ</a><a class="btn btn-outline" href="https://maps.apple.com/?ll=36.4035624,138.2459171&q=%E4%B8%8A%E7%94%B0%E5%9F%8E" target="_blank" rel="noreferrer">Apple マップ</a></div></div></div></section><section class="section section-paper"><div class="container">{section_heading('By train','主要都市から上田駅へ')}<div class="access-cards"><article class="access-card"><h3>東京 → 上田</h3><div class="big">新幹線 約90分</div><p>日帰り可能。</p></article><article class="access-card"><h3>軽井沢 → 上田</h3><div class="big">新幹線／しなの鉄道</div><p>速さか途中の旅かで選択。</p></article><article class="access-card"><h3>長野 → 上田</h3><div class="big">新幹線／しなの鉄道</div><p>上田駅から城まで徒歩で完結。</p></article></div></div></section><section class="section"><div class="container">{section_heading('Parking','北側と南側、目的で選ぶ。')}<div class="grid-2"><article class="card"><div class="card-body"><span class="tag tag-moss">本丸へ穏やか</span><h3>北側駐車場</h3><p><strong>工事・催事などにより利用可能台数が変わる場合があります。</strong></p><p>二の丸・本丸へ高低差を抑えて入りやすい。</p></div></article><article class="card"><div class="card-body"><span class="tag tag-red">尼ヶ淵へ近い</span><h3>南側駐車場</h3><p><strong>83台。</strong></p><p>尼ヶ淵に近い一方、城内へは階段・坂があります。</p></div></article></div><div class="notice" style="margin-top:1.4rem"><span class="notice-icon">料</span><p>通常期は1時間無料、以降100円/時、上限500円。特別期間は3時間500円、上限1,000円の案内。現地表示を優先。</p></div></div></section><section class="section section-dark"><div class="container">{section_heading('Museum hours','公園はいつでも。内部見学は時間を決めて。')}<table class="info-table" style="color:var(--ink)"><tr><th>公園</th><td>24時間／無料／無休</td></tr><tr><th>博物館・南北櫓</th><td>9:00–17:00／最終16:30</td></tr><tr><th>主な休館</th><td>水曜、祝日の翌日、年末年始ほか</td></tr><tr><th>櫓冬季休館</th><td>例年11月中旬頃–翌3月</td></tr><tr><th>共通券</th><td>一般500円、学生300円、小中学生150円</td></tr></table></div></section>'''


def food_page() -> str:
    cards=''.join(f'''<article class="food-card" id="{fid}" data-reveal><img src="{img}" alt="{name}" loading="lazy"><div class="food-card-body"><span class="tag" style="border-color:rgba(255,255,255,.28)">{area}</span><h2>{name}</h2><p>{desc}</p></div></article>''' for fid,name,img,desc,area in FOODS)
    rows=[("信州蕎麦の草笛 上田お城前店","信州そば","城から徒歩約3分","11時頃から昼営業","城のすぐ近く。売切れを当日確認"),("日昌亭","あんかけ焼きそば","城から徒歩約15分","昼中心／水曜休の案内","臨時休業を確認"),("富士アイス","志゛まんやき","城から徒歩約10分","9:30–19:00の案内","売切れ・火曜等に注意"),("つづらや","美味だれ焼き鳥","城から徒歩約12分","17:00–22:00の案内","日曜・祝日休の案内")]
    table=''.join(f'<tr><td><strong>{a}</strong><br><span class="small muted">{b}</span></td><td>{c}</td><td>{d}</td><td>{e}</td></tr>' for a,b,c,d,e in rows)
    return page_hero("Food & town","城下町グルメ","何を食べるかだけでなく、昼・夕方・持ち歩きの時間帯から選ぶ。上田城の前後に無理なく組み込める食のガイドです。") + f'''<section class="section"><div class="container"><div class="food-grid">{cards}</div></div></section><section class="section section-paper"><div class="container">{section_heading('Nearby examples','上田城から歩ける食事候補','固定ランキングではなく、旅程に入れやすい代表例です。出発当日に再確認してください。')}<div style="overflow-x:auto"><table class="restaurant-table"><thead><tr><th>店・ジャンル</th><th>城から</th><th>時間</th><th>注意</th></tr></thead><tbody>{table}</tbody></table></div></div></section><section class="section"><div class="container split reverse">{photo('/images/yanagimachi.webp','柳町','yanagimachi','Suikotei / CC BY 4.0')}<div><span class="eyebrow">Yanagimachi</span><h2 class="section-title">上田城から徒歩約10分、発酵の町へ。</h2><p>旧北国街道の面影を残す通りに、酒、ワイン、味噌、パン、そば、甘味が集まります。</p><p><strong>上田城 → 博物館 → 柳町で昼食 → 海野町 → 上田駅</strong></p><a class="btn btn-ink" href="/routes/#half-day">半日ルートへ</a></div></div></section>'''


def seasons_page() -> str:
    return page_hero("Seasons","四季の上田城","季節が変わると、主役となる場所も歩く順番も変わります。写真だけでなく、混雑・開館・足元まで含めて計画します。") + f'''<section class="section section-dark"><div class="container">{season_switcher()}</div></section><section class="section"><div class="container">{section_heading('Season planner','季節別・先に確認すること')}<div class="grid-4"><article class="card"><div class="card-body"><span class="tag tag-red">春</span><h3>開花と交通規制</h3><p>直前の開花状況と催事日の駐車ルールを優先。</p></div></article><article class="card"><div class="card-body"><span class="tag tag-moss">夏</span><h3>暑さと木陰</h3><p>朝に城内、昼に博物館、午後にケヤキ並木。</p></div></article><article class="card"><div class="card-body"><span class="tag tag-red">秋</span><h3>色づきと冬季休館</h3><p>紅葉と櫓の冬季休館開始を同時に確認。</p></div></article><article class="card"><div class="card-body"><span class="tag">冬</span><h3>凍結と日没</h3><p>階段を無理に使わず、落葉後の城の骨格を見る。</p></div></article></div></div></section><section class="section section-paper"><div class="container grid-2"><article class="card"><div class="card-image wide"><img src="/images/hero-spring.webp" alt="桜の上田城"></div><div class="card-body"><h2>上田城の桜</h2><p>櫓門、本丸堀、尼ヶ淵をつなぐ春の歩き方。</p><a class="btn btn-outline" href="/sakura/">桜ガイド</a></div></article><article class="card"><div class="card-image wide"><img src="/images/autumn.webp" alt="上田城の紅葉"></div><div class="card-body"><h2>上田城の紅葉</h2><p>ケヤキ並木、本丸堀、尼ヶ淵を巡る秋の歩き方。</p><a class="btn btn-outline" href="/autumn/">紅葉ガイド</a></div></article></div></section>'''


def seasonal_detail(kind: str) -> str:
    if kind == 'sakura':
        return page_hero("Sakura","上田城の桜","何日に行くかより、開花状況・光・混雑で歩く順番を決める。櫓門と桜だけで終わらない春のルートです。") + f'''<section class="section"><div class="container split">{photo('/images/hero-spring.webp','桜の東虎口櫓門','spring','Hiroaki Kaneko / CC BY-SA 3.0',True)}<div><span class="eyebrow">Best viewpoints</span><h2 class="section-title">春の主役は、三つの高さ。</h2><p><strong>門前：</strong>東虎口櫓門と枝垂れ桜。<br><strong>堀沿い：</strong>水面、土塁、桜。<br><strong>崖下：</strong>尼ヶ淵から見上げる。</p></div></div></section><section class="section section-paper"><div class="container"><h2 class="section-title">桜の60分ルート</h2><div class="route-card" style="max-width:850px"><div class="route-time"><strong>60</strong><span>MINUTES<br>約1.4km</span></div><div class="route-body"><h3>朝の櫓門から尼ヶ淵へ</h3><p class="route-path">二の丸橋 → 東虎口櫓門 → 本丸堀 → 眞田神社 → 西櫓 → 尼ヶ淵 → ケヤキ並木</p></div></div></div></section><section class="section section-dark"><div class="container grid-3"><article><h2>朝</h2><p>門前の人が少なく柔らかな光。</p></article><article><h2>昼</h2><p>門前は混雑。堀沿いへ分散。</p></article><article><h2>夜</h2><p>ライトアップ時は足元と寒暖差に注意。</p></article></div></section>'''
    return page_hero("Autumn","上田城の紅葉","赤いモミジだけでなく、黄色いケヤキ、暗い水堀、石垣をつなぐ。秋の上田城を立体的に歩きます。") + f'''<section class="section"><div class="container split">{photo('/images/autumn.webp','上田城の紅葉','autumn','Yuya Sekiguchi / CC BY 2.0',True)}<div><span class="eyebrow">Three colors</span><h2 class="section-title">赤、黄、石の灰色を探す。</h2><p><strong>モミジ：</strong>本丸周辺。<br><strong>ケヤキ：</strong>遊歩道。<br><strong>石垣・水堀：</strong>色を引き締める骨格。</p></div></div></section><section class="section section-paper"><div class="container"><h2 class="section-title">紅葉の60分ルート</h2><div class="route-card" style="max-width:850px"><div class="route-time"><strong>60</strong><span>MINUTES<br>約1.6km</span></div><div class="route-body"><h3>ケヤキ並木から本丸、水堀へ</h3><p class="route-path">二の丸橋 → ケヤキ並木 → 東虎口櫓門 → 本丸堀 → 西櫓 → 尼ヶ淵</p></div></div></div></section><section class="section section-dark"><div class="container"><div class="notice" style="background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.2);color:white"><span class="notice-icon">休</span><p>南櫓・北櫓は例年11月中旬頃から翌3月まで冬季休館。紅葉と内部公開の時期がずれる可能性があります。</p></div></div></section>'''


def faq_page() -> str:
    faqs=[("上田城に天守はありますか？","現在、見学できる天守はありません。西櫓、南北櫓、櫓門、土塁、水堀、尼ヶ淵が主な見どころです。"),("公園は無料ですか？","24時間入園でき無料です。博物館と南北櫓内部は有料です。"),("開園時間は？","公園は24時間。博物館・櫓は原則9:00–17:00、最終16:30です。"),("見学時間は？","30分、60分、120分の三つが目安です。"),("西櫓へ入れますか？","内部非公開です。"),("上田駅から歩けますか？","お城口から徒歩約12分です。"),("駐車場は？","北側と南側があります。高低差と目的で選びます。"),("車椅子・ベビーカーは？","北側から本丸へは比較的穏やか。尼ヶ淵の階段は避けられます。"),("雨の日は？","博物館と南北櫓を中心にします。"),("冬でも見学できますか？","公園は見学できますが櫓は冬季休館。凍結に注意。"),("真田幸村との関係は？","真田信繁は父・昌幸と第二次上田合戦に関わりました。"),("真田井戸の抜け穴は本当？","確認された事実ではなく伝承です。"),("桜の見頃は？","年により変わるため直前の開花情報で判断します。"),("ペットは？","現地ルール、リード、混雑への配慮を確認してください。"),("御城印・スタンプは？","頒布・設置場所と時間が変わるため当日案内を確認してください。")]
    details=''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in faqs)
    schema={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
    return page_hero("FAQ","よくある質問","出発前に迷いやすいことを、建物・時間・交通・季節・伝承に分けてまとめました。") + f'''<section class="section"><div class="narrow"><div class="faq">{details}</div><p class="small muted" style="margin-top:1.5rem">営業時間・料金・交通・催事情報は変更されるため、出発前に公式発表をご確認ください。</p></div></section>''', schema


def credits_page() -> str:
    items=[]
    for cid,src,title,author,license_name,license_url,source_url in CREDITS:
        items.append(f'''<article class="credit-item" id="{cid}"><img src="{src}" alt="{title}" loading="lazy"><div><h2>{title}</h2><p><strong>作者：</strong>{author}</p><p><strong>ライセンス：</strong><a href="{license_url}" target="_blank" rel="license noreferrer">{license_name}</a></p><p><strong>加工：</strong>WebP変換、サイズ調整、必要に応じて表示時のトリミング</p><p><a href="{source_url}" target="_blank" rel="noreferrer">Wikimedia Commons の原典ページ</a></p></div></article>''')
    return page_hero("Credits","写真・資料について","写真は再利用条件を確認できる実写素材のみを使用し、作者・ライセンス・加工内容を一枚ずつ記録しています。") + f'''<section class="section"><div class="container"><div class="notice" style="margin-bottom:2rem"><span class="notice-icon">写</span><p>写真の著作権は各作者に帰属します。サイトコードのMITライセンスには写真は含まれません。</p></div><div class="credit-list">{''.join(items)}</div></div></section><section class="section section-paper"><div class="narrow prose"><h2>資料の扱い</h2><p>歴史、施設、料金、交通、駐車場は上田市、上田市立博物館、信州上田観光協会などの公開情報を中心に確認しています。</p><h2>非公式サイト</h2><p>本サイトは自治体・神社・観光協会の公式サイトではありません。ロゴも独自制作です。</p></div></section>'''


def write_page(path: str, title: str, desc: str, body: str, schema=None, noindex=False) -> None:
    if path == "/": out = DIST / "index.html"
    elif path == "/404.html": out = DIST / "404.html"
    else: out = DIST / path.strip("/") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(layout(path, title, desc, body, schema, noindex), encoding="utf-8")


def main() -> None:
    if DIST.exists(): shutil.rmtree(DIST)
    shutil.copytree(PUBLIC, DIST)
    tourist_schema={"@context":"https://schema.org","@type":"TouristAttraction","name":"上田城跡公園","alternateName":"上田城","address":{"@type":"PostalAddress","addressRegion":"長野県","addressLocality":"上田市","streetAddress":"二の丸6263番地イ","addressCountry":"JP"},"geo":{"@type":"GeoCoordinates","latitude":36.4035624,"longitude":138.2459171},"isAccessibleForFree":True,"publicAccess":True}
    write_page("/","上田城を歩く","真田昌幸が築いた上田城を、歴史・地形・建築・城下町の視点から歩く現地ガイド。",home(),tourist_schema)
    write_page("/history/","上田城の歴史","真田昌幸の築城、二度の上田合戦、破城、仙石氏の復興、櫓の再移築まで。",history_page())
    write_page("/highlights/","上田城の見どころ","東虎口櫓門、西櫓、尼ヶ淵、眞田神社、真田井戸、土塁、水堀など12の見どころ。",highlights_page())
    write_page("/routes/","上田城の散策ルート","30分・60分・120分、柳町までの半日コース、段差を減らしたルート。",routes_page())
    write_page("/access/","アクセス・駐車場","上田駅からの徒歩、鉄道、上田菅平IC、北側・南側駐車場を解説。",access_page())
    write_page("/food/","上田城周辺のグルメ","美味だれ焼き鳥、上田あんかけ焼きそば、信州そば、柳町の食を紹介。",food_page())
    write_page("/seasons/","四季の上田城","春の桜、夏のケヤキ、秋の紅葉、冬の地形観察。",seasons_page())
    write_page("/sakura/","上田城の桜","桜の撮影場所、朝・昼・夜の歩き方、混雑と駐車場の注意。",seasonal_detail('sakura'))
    write_page("/autumn/","上田城の紅葉","紅葉スポット、ケヤキ並木、本丸堀、尼ヶ淵の歩き方。",seasonal_detail('autumn'))
    faq_body, faq_schema = faq_page()
    write_page("/faq/","よくある質問","上田城の天守、料金、時間、所要時間、駐車場、冬季休館など。",faq_body,faq_schema)
    write_page("/credits/","写真・資料について","Wikimedia Commons写真の作者、ライセンス、加工内容。",credits_page())
    not_found='''<section class="page-hero" style="min-height:70vh;display:grid;align-items:center"><div class="container"><span class="eyebrow">404</span><h1 class="display-title">道を一本、違えたようです。</h1><p>このページは移動したか、まだ城下図に描かれていません。</p><a class="btn btn-primary" href="/">上田城の入口へ戻る</a></div></section>'''
    write_page("/404.html","ページが見つかりません","ページが見つかりません。",not_found,noindex=True)
    paths=["/","/history/","/highlights/","/routes/","/access/","/food/","/seasons/","/sakura/","/autumn/","/faq/","/credits/"]
    sitemap='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{SITE}{p}</loc><changefreq>{"weekly" if p=="/" else "monthly"}</changefreq><priority>{"1.0" if p=="/" else "0.8"}</priority></url>' for p in paths)+'</urlset>'
    (DIST/'sitemap.xml').write_text(sitemap,encoding='utf-8')
    print(f"Built {len(paths)+1} HTML pages in {DIST}")

if __name__ == "__main__":
    main()
