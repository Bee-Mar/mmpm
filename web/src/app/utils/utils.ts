import {getCookie, setCookie} from "typescript-cookie";

export function get_cookie(name: string, default_value: string): string {
  if (default_value && !getCookie(name)) {
    set_cookie(name, default_value);
  }

  return String(getCookie(name));
}

export function set_cookie(name: string, value: string) {
  setCookie(name, String(value), {expires: 1825, path: ""});
}

export function open_url(address: string) {
  window.open(address, "_blank");
}
