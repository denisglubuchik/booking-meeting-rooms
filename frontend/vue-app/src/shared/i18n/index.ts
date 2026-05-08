import { createI18n } from "vue-i18n";
import { en } from "./locales/en";
import { ru } from "./locales/ru";

const DEFAULT_LOCALE = "ru";

function resolveInitialLocale() {
  const saved = localStorage.getItem("booking_locale");
  if (saved === "ru" || saved === "en") return saved;
  return DEFAULT_LOCALE;
}

export const i18n = createI18n({
  legacy: false,
  locale: resolveInitialLocale(),
  fallbackLocale: "ru",
  messages: {
    ru,
    en,
  },
});

export function setLocale(locale: "ru" | "en") {
  i18n.global.locale.value = locale;
  localStorage.setItem("booking_locale", locale);
}
