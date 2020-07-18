import * as Cookie from "js-cookie";
import { Injectable } from "@angular/core";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";
import { ActiveProcessCountService } from "src/app/services/active-process-count.service";

@Injectable({
  providedIn: "root"
})
export class MMPMUtility {
  constructor(public activeProcessService: ActiveProcessCountService){}

  public isSamePackage(a: MagicMirrorPackage, b: MagicMirrorPackage): boolean {
      return a.title === b.title && a.repository === b.repository && a.author === b.author;
  }

  public isSamePackageStrictComparison(a: MagicMirrorPackage, b: MagicMirrorPackage): boolean {
    return a.title === b.title && a.repository === b.repository && a.author === b.author && a.category === b.category;
  }

  public getCookie(name: string): Object {
    return Cookie.get(name);
  }

  public setCookie(name: string, value: any) {
    Cookie.set(name, String(value), {expires: 1825, path: ""});
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

  public saveProcessIds(pkgs: MagicMirrorPackage[], action: string): Array<number> {
    let ids: Array<number> = new Array<number>();

    for (let pkg of pkgs) {
      ids.push(this.activeProcessService.insertProcess({
        name: pkg.title,
        action,
        startTime: Date().toString()
      }));
    }

    return ids;
  }

  public deleteProcessIds(ids: Array<number>): void {
    for (let id of ids) {
      if (!this.activeProcessService.removeProcess(id)) {
        console.log(`Failed to remove process ${id}`);
      }
    }
  }

  public openUrl(url: string) {
    window.open(url, '_blank');
  }

}
