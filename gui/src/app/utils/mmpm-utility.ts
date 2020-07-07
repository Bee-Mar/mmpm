import * as Cookie from "js-cookie";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";

export class MMPMUtility {
  constructor(){}

  public isSamePackage(a: MagicMirrorPackage, b: MagicMirrorPackage, strictEquality: boolean = false): boolean {
    if (!strictEquality)
      return a.title === b.title && a.repository === b.repository && a.author === b.author;
    return a.title === b.title && a.repository === b.repository && a.author === b.author && a.category === b.category;
  }

  public getCookie(name: string): Object {
    return Cookie.get(name);
  }

  public setCookie(name: string, value: any) {
    Cookie.set(name, String(value), {expires: 14, path: ""});
  }

  public basicDialogSettings(data?: any): object {
    return data ? {
      width: "75vw",
      height: "75vh",
      disableClose: true,
      data
    } : {
      width: "75vw",
      height: "75vh",
      disableClose: true
    };
  }
}
