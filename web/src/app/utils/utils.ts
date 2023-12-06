import { getCookie, setCookie } from "typescript-cookie";

export function get_cookie(name: string): string {
  return getCookie(name) || "";
}

export function set_cookie(name: string, value: string) {
  setCookie(name, String(value), { expires: 1825, path: "" });
}

export function open_url(address: string) {
  window.open(address, "_blank");
}
