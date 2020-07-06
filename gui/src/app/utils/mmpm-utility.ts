import * as Cookie from "js-cookie";

export class MMPMUtility {
  constructor(){}

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
