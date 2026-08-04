(() => {
  const doc = document;
  const storage = {
    get(key) {
      try { return window.localStorage.getItem(key); } catch { return null; }
    },
    set(key, value) {
      try { window.localStorage.setItem(key, value); } catch { /* storage may be disabled */ }
    },
  };

  const menuButton = doc.querySelector("[data-menu-button]");
  const menu = doc.querySelector("[data-menu]");
  if (menuButton instanceof HTMLButtonElement && menu instanceof HTMLElement) {
    menuButton.addEventListener("click", () => {
      const open = menuButton.getAttribute("aria-expanded") === "true";
      menuButton.setAttribute("aria-expanded", String(!open));
      menu.dataset.open = String(!open);
      doc.body.classList.toggle("menu-open", !open);
    });
  }

  const reveal = () => {
    const elements = [...doc.querySelectorAll("[data-reveal]")];
    if (!("IntersectionObserver" in window)) {
      elements.forEach((element) => element.classList.add("is-visible"));
      return;
    }
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8%", threshold: 0.08 });
    elements.forEach((element) => observer.observe(element));
  };
  reveal();

  const seasonRoot = doc.querySelector("[data-season-switcher]");
  if (seasonRoot instanceof HTMLElement) {
    const buttons = [...seasonRoot.querySelectorAll("[data-season]")];
    const panels = [...seasonRoot.querySelectorAll("[data-season-panel]")];
    const setSeason = (season) => {
      buttons.forEach((button) => {
        const active = button.getAttribute("data-season") === season;
        button.setAttribute("aria-selected", String(active));
      });
      panels.forEach((panel) => {
        const active = panel.getAttribute("data-season-panel") === season;
        panel.toggleAttribute("hidden", !active);
      });
    };
    buttons.forEach((button) => button.addEventListener("click", () => setSeason(button.getAttribute("data-season") || "spring")));
  }

  const checklist = doc.querySelector("[data-spot-checklist]");
  if (checklist instanceof HTMLElement) {
    const storageKey = "ueda-castle-spots";
    const boxes = [...checklist.querySelectorAll('input[type="checkbox"][data-spot-id]')];
    const count = checklist.querySelector("[data-check-count]");
    const share = checklist.querySelector("[data-share-spots]");
    const reset = checklist.querySelector("[data-reset-spots]");
    let saved = [];
    try {
      saved = JSON.parse(storage.get(storageKey) || "[]");
      if (!Array.isArray(saved)) saved = [];
    } catch { saved = []; }
    const params = new URLSearchParams(location.search);
    const fromUrl = (params.get("spots") || "").split(",").filter(Boolean);
    if (fromUrl.length) saved = fromUrl;
    boxes.forEach((box) => {
      if (box instanceof HTMLInputElement) box.checked = saved.includes(box.dataset.spotId || "");
    });
    const sync = () => {
      const selected = boxes.filter((box) => box instanceof HTMLInputElement && box.checked).map((box) => box.getAttribute("data-spot-id"));
      storage.set(storageKey, JSON.stringify(selected));
      if (count) count.textContent = String(selected.length);
      return selected;
    };
    boxes.forEach((box) => box.addEventListener("change", sync));
    sync();
    if (share instanceof HTMLButtonElement) {
      share.addEventListener("click", async () => {
        const url = new URL(location.href);
        const selected = sync();
        if (selected.length) url.searchParams.set("spots", selected.join(",")); else url.searchParams.delete("spots");
        const text = "上田城で歩きたい場所をまとめました。";
        try {
          if (navigator.share) await navigator.share({ title: "上田城の散策リスト", text, url: url.toString() });
          else {
            await navigator.clipboard.writeText(url.toString());
            share.textContent = "リンクをコピーしました";
            setTimeout(() => { share.textContent = "リストを共有"; }, 2200);
          }
        } catch { /* user cancelled */ }
      });
    }
    if (reset instanceof HTMLButtonElement) {
      reset.addEventListener("click", () => {
        boxes.forEach((box) => { if (box instanceof HTMLInputElement) box.checked = false; });
        sync();
      });
    }
  }

  const planner = doc.querySelector("[data-route-planner]");
  if (planner instanceof HTMLFormElement) {
    const result = planner.querySelector("[data-route-result]");
    const title = planner.querySelector("[data-route-title]");
    const path = planner.querySelector("[data-route-path]");
    const note = planner.querySelector("[data-route-note]");
    const share = planner.querySelector("[data-share-route]");
    const choose = () => {
      const data = new FormData(planner);
      const minutes = Number(data.get("time") || 60);
      const museum = data.get("museum") === "on";
      const food = String(data.get("food") || "none");
      const gentle = data.get("gentle") === "on";
      let routeTitle = "60分・城の輪郭を読む標準コース";
      let routePath = "二の丸橋 → 東虎口櫓門 → 真田石 → 眞田神社 → 真田井戸 → 西櫓 → 尼ヶ淵";
      let routeNote = "初めての上田城に。櫓門だけでなく、城を守った地形まで歩きます。";
      if (minutes <= 30) {
        routeTitle = "30分・代表景観をつなぐ短縮コース";
        routePath = "二の丸橋 → 東虎口櫓門 → 真田石 → 眞田神社 → 西櫓";
        routeNote = "移動の合間に、上田城らしい景観を無理なく押さえる構成です。";
      } else if (minutes >= 120 || museum) {
        routeTitle = "120分・建物と歴史を深掘るコース";
        routePath = "東虎口櫓門 → 南櫓・北櫓 → 本丸 → 西櫓 → 尼ヶ淵 → 上田市立博物館 → ケヤキ並木";
        routeNote = "博物館・櫓の開館時間と休館日を確認して出発してください。";
      }
      if (gentle) {
        routePath = "北側駐車場／二の丸橋 → 東虎口櫓門 → 本丸 → 眞田神社 → 西櫓外観 → 二の丸";
        routeNote += " 段差を減らし、尼ヶ淵の階段を避けるルートに調整しました。";
      }
      if (food === "yanagimachi") routePath += " → 柳町（発酵食・甘味）";
      if (food === "soba") routePath += " → 大手・中央エリア（信州そば）";
      if (title) title.textContent = routeTitle;
      if (path) path.textContent = routePath;
      if (note) note.textContent = routeNote;
      if (result instanceof HTMLElement) result.hidden = false;
      const url = new URL(location.href);
      url.searchParams.set("time", String(minutes));
      url.searchParams.set("museum", museum ? "1" : "0");
      url.searchParams.set("food", food);
      url.searchParams.set("gentle", gentle ? "1" : "0");
      history.replaceState({}, "", url);
      storage.set("ueda-castle-route", JSON.stringify({ minutes, museum, food, gentle }));
      return url.toString();
    };
    planner.addEventListener("submit", (event) => { event.preventDefault(); choose(); });
    const params = new URLSearchParams(location.search);
    let initial = null;
    if (params.has("time")) initial = { minutes: Number(params.get("time")), museum: params.get("museum") === "1", food: params.get("food") || "none", gentle: params.get("gentle") === "1" };
    else {
      try { initial = JSON.parse(storage.get("ueda-castle-route") || "null"); } catch { initial = null; }
    }
    if (initial) {
      const timeInput = planner.querySelector(`[name="time"][value="${initial.minutes}"]`);
      if (timeInput instanceof HTMLInputElement) timeInput.checked = true;
      const museumInput = planner.querySelector('[name="museum"]');
      if (museumInput instanceof HTMLInputElement) museumInput.checked = Boolean(initial.museum);
      const foodInput = planner.querySelector(`[name="food"][value="${initial.food}"]`);
      if (foodInput instanceof HTMLInputElement) foodInput.checked = true;
      const gentleInput = planner.querySelector('[name="gentle"]');
      if (gentleInput instanceof HTMLInputElement) gentleInput.checked = Boolean(initial.gentle);
      choose();
    }
    if (share instanceof HTMLButtonElement) {
      share.addEventListener("click", async () => {
        const url = choose();
        try {
          if (navigator.share) await navigator.share({ title: "上田城の散策ルート", url });
          else {
            await navigator.clipboard.writeText(url);
            share.textContent = "リンクをコピーしました";
            setTimeout(() => { share.textContent = "このルートを共有"; }, 2200);
          }
        } catch { /* user cancelled */ }
      });
    }
  }

  doc.querySelectorAll("[data-map-pin]").forEach((pin) => {
    const activate = () => {
      const id = pin.getAttribute("data-map-pin");
      doc.querySelectorAll("[data-map-card]").forEach((card) => card.toggleAttribute("hidden", card.getAttribute("data-map-card") !== id));
      doc.querySelectorAll("[data-map-pin]").forEach((other) => other.setAttribute("aria-pressed", String(other === pin)));
    };
    pin.addEventListener("click", activate);
    pin.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        activate();
      }
    });
  });

  if ("serviceWorker" in navigator && location.protocol === "https:") {
    window.addEventListener("load", () => navigator.serviceWorker.register("/sw.js").catch(() => undefined));
  }
})();
