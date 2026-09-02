/**
 * Lightweight, local-first bilingual i18n engine (zh-Hant / en) for Obsidian Property Studio v1.1.0.
 * Zero CDN dependencies, offline-first with localStorage preference.
 */
const I18N = {
  currentLocale: "zh-Hant",
  locales: {
    "zh-Hant": {},
    "en": {}
  },

  async init(defaultLocale = "zh-Hant") {
    const saved = localStorage.getItem("ps_locale") || defaultLocale;
    this.currentLocale = saved;
    try {
      const [zh, en] = await Promise.all([
        fetch("/locales/zh-Hant.json").then(r => r.json()).catch(() => ({})),
        fetch("/locales/en.json").then(r => r.json()).catch(() => ({}))
      ]);
      if (zh && Object.keys(zh).length) this.locales["zh-Hant"] = zh;
      if (en && Object.keys(en).length) this.locales["en"] = en;
    } catch (e) {
      console.warn("i18n fetch fallback", e);
    }
    this.applyLocale(this.currentLocale);
  },

  t(key, params = {}) {
    const dict = this.locales[this.currentLocale] || this.locales["zh-Hant"] || {};
    let text = dict[key] || (this.locales["en"] ? this.locales["en"][key] : key) || key;
    if (typeof text !== "string") return key;
    for (const [k, v] of Object.entries(params)) {
      text = text.replace(new RegExp(`\\{${k}\\}`, "g"), v);
    }
    return text;
  },

  setLocale(locale) {
    if (!["zh-Hant", "en"].includes(locale)) return;
    this.currentLocale = locale;
    localStorage.setItem("ps_locale", locale);
    this.applyLocale(locale);
  },

  toggleLocale() {
    const next = this.currentLocale === "zh-Hant" ? "en" : "zh-Hant";
    this.setLocale(next);
  },

  applyLocale(locale) {
    document.documentElement.setAttribute("lang", locale);
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.getAttribute("data-i18n");
      const trans = this.t(key);
      if (trans && trans !== key) el.textContent = trans;
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
      const key = el.getAttribute("data-i18n-placeholder");
      const trans = this.t(key);
      if (trans && trans !== key) el.setAttribute("placeholder", trans);
    });
    document.querySelectorAll("[data-i18n-title]").forEach(el => {
      const key = el.getAttribute("data-i18n-title");
      const trans = this.t(key);
      if (trans && trans !== key) el.setAttribute("title", trans);
    });
    const langBtn = document.getElementById("langToggleBtn");
    if (langBtn) {
      langBtn.textContent = locale === "zh-Hant" ? "EN" : "繁中";
      langBtn.title = locale === "zh-Hant" ? "Switch to English" : "切換至繁體中文";
    }
  }
};

window.I18N = I18N;
window.t = (k, p) => I18N.t(k, p);
