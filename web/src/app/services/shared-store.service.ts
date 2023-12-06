import { Injectable } from "@angular/core";
import { BehaviorSubject, Observable } from "rxjs";
import { MagicMirrorPackage } from "@/magicmirror/models/magicmirror-package";
import { MagicMirrorPackageAPI } from "./api/magicmirror-package-api.service";
import { APIResponse } from "@/services/api/base-api";

@Injectable({
  providedIn: "root",
})
export class SharedStoreService {
  constructor(private mm_pkg_api: MagicMirrorPackageAPI) {}

  private packages_subj: BehaviorSubject<MagicMirrorPackage[]> = new BehaviorSubject<Array<MagicMirrorPackage>>([]);
  public readonly packages: Observable<MagicMirrorPackage[]> = this.packages_subj.asObservable();

  public get_packages(): void {
    console.log("Getting packages for data store");

    this.mm_pkg_api.get_packages().then((response: APIResponse) => {
      this.packages_subj.next(response.message as Array<MagicMirrorPackage>);
      console.log("Retrieved packages");
    });
  }
}
