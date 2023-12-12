import {Injectable} from "@angular/core";
import {BehaviorSubject, Observable} from "rxjs";
import {MagicMirrorPackage} from "@/models/magicmirror-package";
import {MagicMirrorPackageAPI} from "./api/magicmirror-package-api.service";
import {APIResponse} from "@/services/api/base-api";
import {DatabaseInfo} from "@/models/database-info";
import {UpgradableDetails} from "@/models/upgradable-details";
import {MMPMEnv} from '@/models/mmpm-env';

@Injectable({
  providedIn: "root",
})
export class SharedStoreService {
  constructor(private mmPkgApi: MagicMirrorPackageAPI) {}

  private packagesSubj: BehaviorSubject<MagicMirrorPackage[]> = new BehaviorSubject<Array<MagicMirrorPackage>>([]);
  public readonly packages: Observable<MagicMirrorPackage[]> = this.packagesSubj.asObservable();

  private dbInfoSubj: BehaviorSubject<DatabaseInfo> = new BehaviorSubject<DatabaseInfo>({});
  public readonly dbInfo: Observable<DatabaseInfo> = this.dbInfoSubj.asObservable();

  private upgradeableSubj: BehaviorSubject<UpgradableDetails> = new BehaviorSubject<UpgradableDetails>({mmpm: false, MagicMirror: false, packages: []});
  public readonly upgradable: Observable<UpgradableDetails> = this.upgradeableSubj.asObservable();

  private envSubj: BehaviorSubject<MMPMEnv> = new BehaviorSubject<MMPMEnv>({
    MMPM_IS_DOCKER_IMAGE: false,
    MMPM_LOG_LEVEL: "",
    MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE: "",
    MMPM_MAGICMIRROR_PM2_PROCESS_NAME: "",
    MMPM_MAGICMIRROR_ROOT: "",
    MMPM_MAGICMIRROR_URI: "",
  });

  public readonly env: Observable<MMPMEnv> = this.envSubj.asObservable();

  public load(): void {
    console.log("Getting packages for data store");

    this.mmPkgApi.get_("env").then((response: APIResponse) => {
      if (response.code === 200) {
        this.envSubj.next(response.message as MMPMEnv);
      } else {
        console.log(response.message);
      }
    });

    this.mmPkgApi.getPackages().then((response: APIResponse) => {
      if (response.code === 200) {
        this.packagesSubj.next(response.message as Array<MagicMirrorPackage>);
        console.log("Retrieved packages");
      } else {
        this.packagesSubj.next([]);
        console.log(response.message);
      }

      this.mmPkgApi.get_("db/info").then((response: APIResponse) => {
        if (response.code === 200) {
          this.dbInfoSubj.next(response.message as DatabaseInfo);
        } else {
          console.log(response.message);
          this.dbInfoSubj.next({last_update: "N/A", categories: 0, packages: 0});
        }
      });

      this.mmPkgApi.get_("db/upgradable").then((response: APIResponse) => {
        if (response.code === 200) {
          this.upgradeableSubj.next(response.message as UpgradableDetails);
        } else {
          console.log(response.message);
          this.upgradeableSubj.next({mmpm: false, MagicMirror: false, packages: []});
        }
      });
    });
  }
}
