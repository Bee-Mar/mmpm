import { Injectable } from "@angular/core";
import { BehaviorSubject, Observable } from "rxjs";
import { MagicMirrorPackage } from "@/models/magicmirror-package";
import { MagicMirrorPackageAPI } from "./api/magicmirror-package-api.service";
import { APIResponse } from "@/services/api/base-api";
import { DatabaseInfo } from "@/models/database-details";

@Injectable({
  providedIn: "root",
})
export class SharedStoreService {
  constructor(private mmPkgApi: MagicMirrorPackageAPI) {}

  private packagesSubj: BehaviorSubject<MagicMirrorPackage[]> = new BehaviorSubject<Array<MagicMirrorPackage>>([]);
  public readonly packages: Observable<MagicMirrorPackage[]> = this.packagesSubj.asObservable();

  private dbInfoSubj: BehaviorSubject<DatabaseInfo> = new BehaviorSubject<DatabaseInfo>({});
  public readonly dbInfo: Observable<DatabaseInfo> = this.dbInfoSubj.asObservable();

  public getPackages(): void {
    console.log("Getting packages for data store");

    this.mmPkgApi.getPackages().then((response: APIResponse) => {
      if (response.code === 200) {
        this.packagesSubj.next(response.message as Array<MagicMirrorPackage>);
        console.log("Retrieved packages");
      } else {
        console.log(response.message);
      }

      this.mmPkgApi.get_("db/info").then((response: APIResponse) => {
        if (response.code === 200) {
          this.dbInfoSubj.next(response.message as DatabaseInfo);
        } else {
          console.log(response.message);
        }
      });
    });
  }
}
