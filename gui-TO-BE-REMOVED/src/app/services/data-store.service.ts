import { Injectable } from "@angular/core";
import { BehaviorSubject, Observable } from "rxjs";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";
import { RestApiService } from "src/app/services/rest-api.service";
import { MMPMUtility } from "src/app/utils/mmpm-utility";
import { URLS } from "src/app/utils/urls";

@Injectable({
  providedIn: "root",
})
export class DataStoreService {
  constructor(private api: RestApiService, private mmpmUtility: MMPMUtility) {}

  private _marketplacePackages: BehaviorSubject<MagicMirrorPackage[]> = new BehaviorSubject<Array<MagicMirrorPackage>>([]);
  private _installedPackages: BehaviorSubject<MagicMirrorPackage[]> = new BehaviorSubject<Array<MagicMirrorPackage>>([]);
  private _externalPackages: BehaviorSubject<MagicMirrorPackage[]> = new BehaviorSubject<Array<MagicMirrorPackage>>([]);
  private _availableUpgrades: BehaviorSubject<Object> = new BehaviorSubject<Object>({});
  private _mmpmEnvironmentVariables: BehaviorSubject<Map<string, string>> = new BehaviorSubject<Map<string, string>>(new Map<string, string>());
  private _upgradablePackages: BehaviorSubject<any> = new BehaviorSubject<any>({});

  public readonly marketplacePackages: Observable<MagicMirrorPackage[]> = this._marketplacePackages.asObservable();
  public readonly installedPackages: Observable<MagicMirrorPackage[]> = this._installedPackages.asObservable();
  public readonly externalPackages: Observable<MagicMirrorPackage[]> = this._externalPackages.asObservable();
  public readonly availableUpgrades: Observable<Object> = this._availableUpgrades.asObservable();
  public readonly mmpmEnvironmentVariables: Observable<Map<string, string>> = this._mmpmEnvironmentVariables.asObservable();
  public readonly upgradablePackages: Observable<any> = this._upgradablePackages.asObservable();

  public ngOnInit() {}

  private fill(data: any): Array<MagicMirrorPackage> {
    let array = new Array<MagicMirrorPackage>();

    Object.keys(data).forEach((_category) => {
      if (data) {
        for (const pkg of data[_category]) {
          array.push({
            category: _category,
            title: pkg["title"],
            description: pkg["description"],
            author: pkg["author"],
            repository: pkg["repository"],
            directory: pkg["directory"],
          });
        }
      }
    });

    return array;
  }

  public retrieveMagicMirrorPackageData(update: boolean = true): void {
    this.api
      .retrieve(URLS.GET.MMPM.ENVIRONMENT_VARS)
      .then((envVars: any) => {
        let tempMap = new Map<string, string>();
        Object.keys(envVars).forEach((key) => tempMap.set(key, envVars[key]));
        this._mmpmEnvironmentVariables?.next(tempMap);
      })
      .catch((error) => console.log(error));

    this.api
      .retrieve(URLS.GET.PACKAGES.MARKETPLACE)
      .then((marketplace: Array<object>) => {
        this.api
          .retrieve(URLS.GET.PACKAGES.INSTALLED)
          .then((installed: Array<object>) => {
            this.api
              .retrieve(URLS.GET.PACKAGES.EXTERNAL)
              .then((external: Array<object>) => {
                let externalPkgs: Array<MagicMirrorPackage> = this.fill(external);
                let installedPkgs: Array<MagicMirrorPackage> = this.fill(installed);
                let marketplacePkgs: Array<MagicMirrorPackage> = this.fill(marketplace);

                let allPackagesInDatabase: Array<MagicMirrorPackage> = [...marketplacePkgs, ...externalPkgs];

                // removing all the packages that are currently installed from the list of available packages
                for (const installedPkg of installedPkgs) {
                  let index: number = allPackagesInDatabase?.findIndex((available: MagicMirrorPackage) => {
                    return this.mmpmUtility?.isSamePackageStrictComparison(available, installedPkg);
                  });

                  if (index > -1) {
                    allPackagesInDatabase?.splice(index, 1);
                  }
                }

                this._marketplacePackages?.next(allPackagesInDatabase);
                this._installedPackages?.next(installedPkgs);
                this._externalPackages?.next(externalPkgs);

                if (update) {
                  this.api
                    .retrieve(URLS.GET.PACKAGES.UPDATE)
                    .then((_) => {
                      this.api
                        .retrieve(URLS.GET.PACKAGES.UPGRADABLE)
                        .then((upgradable) => {
                          this._upgradablePackages?.next(upgradable);
                        })
                        .catch((error) => console.log(error));
                    })
                    .catch((error) => console.log(error));
                }
              })
              .catch((error) => console.log(error));
          })
          .catch((error) => console.log(error));
      })
      .catch((error) => console.log(error));
  }
}
