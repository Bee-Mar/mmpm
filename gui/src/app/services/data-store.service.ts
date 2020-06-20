import { Injectable } from "@angular/core";
import { MagicMirrorPackage } from "src/app/interfaces/magic-mirror-package";
import { RestApiService } from "src/app/services/rest-api.service";
import { URL } from "src/app/utils/urls";

@Injectable({
  providedIn: "root"
})
export class DataStoreService {

  private availablePackages: Array<MagicMirrorPackage>;
  private installedPackages: Array<MagicMirrorPackage>;
  private externalPackages: Array<MagicMirrorPackage>;

  constructor(private api: RestApiService) {}

  public ngOnInit(): void {}

  private retrievePackages(url: string): Array<MagicMirrorPackage> {
    let packages = new Array<MagicMirrorPackage>();

    this.api.retrieve(`/${url}`).subscribe((pkgs) => {
      Object.keys(pkgs).forEach((_category) => {
        if (pkgs) {
          for (const pkg of pkgs[_category]) {
            packages.push({
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
    });

    return packages;
  }

  public getAllAvailablePackages(): MagicMirrorPackage[] {
    if (!this.availablePackages) this.availablePackages = this.retrievePackages(URL.ALL_AVAILABLE_MODULES);
    return this.availablePackages;
  }

  public getAllInstalledPackages(): Array<MagicMirrorPackage> {
    if (!this.installedPackages) this.installedPackages = this.retrievePackages("all-installed-modules");
    return this.installedPackages;
  }

  public getAllExternalPackages(): MagicMirrorPackage[] {
    if (!this.externalPackages) this.externalPackages = this.retrievePackages("all-external-modules");
    return this.externalPackages;
  }

  public refreshAllAvailablePackages(): void {
    this.availablePackages = this.retrievePackages(URL.ALL_AVAILABLE_MODULES);
  }

  public refreshExternalPackages(): void {
    this.externalPackages = this.retrievePackages("all-external-modules");
  }

  public refreshAllInstalledPackages(): void {
    this.externalPackages = this.retrievePackages("all-installed-modules");
  }
}
