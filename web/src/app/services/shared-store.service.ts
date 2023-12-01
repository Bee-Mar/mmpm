import {Injectable} from '@angular/core';
import {BehaviorSubject, Observable} from "rxjs";
import {MagicMirrorPackage} from "@/magicmirror/models/magicmirror-package";
import {MagicMirrorPackageAPI} from './api/magicmirror-package-api.service';
import {APIResponse} from '@/services/api/base-api';
import {MagicMirrorDatabaseAPI} from './api/magicmirror-database-api.service';

@Injectable({
  providedIn: 'root'
})
export class SharedStoreService {
  constructor(private mm_pkg_api: MagicMirrorPackageAPI, private mm_db_api: MagicMirrorDatabaseAPI) {}

  private packages_subj: BehaviorSubject<MagicMirrorPackage[]> = new BehaviorSubject<Array<MagicMirrorPackage>>([]);
  public readonly packages: Observable<MagicMirrorPackage[]> = this.packages_subj.asObservable();

  public get_packages(): void {
    this.mm_db_api.load().then((response: APIResponse) => {

      if (response.message === true) {
        console.log("Database successfully loaded");

        this.mm_pkg_api.get_packages().then((response: APIResponse) => {
          this.packages_subj.next(response.message);
          console.log("Retrieved packages");
        });
      } else {
        console.log("Unable to load database");
      }
    });
  }
}
