import { Injectable } from "@angular/core";
import { MagicMirrorPackage } from "src/app/interfaces/magic-mirror-package";
import { RestApiService } from "src/app/services/rest-api.service";
import { URL } from "src/app/utils/urls";

@Injectable({
  providedIn: "root"
})
export class DataStoreService {
  private availablePackages: MagicMirrorPackage[];
  private installedPackages: MagicMirrorPackage[];
  private externalPackages: MagicMirrorPackage[];

  constructor(private api: RestApiService) {}

  public ngOnInit(): void {
    this.availablePackages = new Array<MagicMirrorPackage>();
    this.installedPackages = new Array<MagicMirrorPackage>();
    this.externalPackages = new Array<MagicMirrorPackage>();

    this.refreshAllAvailablePackages();
    this.refreshAllInstalledPackages();
    this.refreshAllExternalPackages();
  }

  private fill(data: any, array: MagicMirrorPackage[]) {
    array = new Array<MagicMirrorPackage>();

    Object.keys(data).forEach((_category) => {
      if (data) {
        for (const pkg of data[_category]) {
          array.push({
            category: _category,
            title: pkg["title"],
            description: pkg["description"],
            author: pkg["author"],
            repository: pkg["repository"],
            directory: pkg["directory"] ?? ""
          });
        }
      }
    });
  }

  public getAllAvailablePackages(): MagicMirrorPackage[] {
    if (!this.availablePackages) this.refreshAllAvailablePackages();
    return this.availablePackages;
  }

  public refreshAllAvailablePackages(): void {
    this.api.retrieve(URL.ALL_AVAILABLE_MODULES).then((data) => {
      this.fill(data, this.availablePackages);
      console.log(this.availablePackages);
    }).catch((error) => {
      console.log(error);
    });
  }

  public getAllInstalledPackages(): MagicMirrorPackage[] {
    if (!this.installedPackages) this.refreshAllInstalledPackages();
    return this.installedPackages;
  }

  public refreshAllInstalledPackages(): void {
    this.api.retrieve(URL.ALL_INSTALLED_MODULES).then((data) => {
      this.fill(data, this.installedPackages);
      console.log(this.installedPackages);
    }).catch((error) => {
      console.log(error);
    });
  }

  public getAllExternalPackages(): MagicMirrorPackage[] {
    if (!this.externalPackages) this.refreshAllExternalPackages();
    return this.externalPackages;
  }

  public refreshAllExternalPackages(): void {
    this.api.retrieve(URL.ALL_EXTERNAL_MODULES).then((data) => {
      this.fill(data, this.installedPackages);
      console.log(this.externalPackages);
    }).catch((error) => {
      console.log(error);
    });
  }
}
