import { getCookie as _getCookie, setCookie as _setCookie } from "typescript-cookie";

export function getCookie(name: string, default_value: string): string {
  if (default_value && !_getCookie(name)) {
    setCookie(name, default_value);
  }

  return String(_getCookie(name));
}

export function setCookie(name: string, value: string) {
  _setCookie(name, String(value), { expires: 1825, path: "" });
}

export function openUrl(address: string) {
  window.open(address, "_blank");
}
