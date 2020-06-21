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

  private fillArray(data: any): Array<MagicMirrorPackage> {
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
            directory: pkg["directory"] ?? ""
          });
        }
      }
    });

    return array;
  }

  public getAllAvailablePackages(): Promise<MagicMirrorPackage[]> {
    let promise = new Promise<MagicMirrorPackage[]>((resolve, reject) => {

      if (this.availablePackages?.length) resolve(this.availablePackages);

      this.api.retrieve(URL.ALL_AVAILABLE_MODULES).then((data) => {
        this.availablePackages = this.fillArray(data);
        resolve(this.availablePackages);

      }).catch((error) => {
        console.log(error);
        reject(new Array<MagicMirrorPackage>());
      });
    });

    return promise;
  }

  public refreshAllAvailablePackages(): Promise<boolean> {
    let promise = new Promise<boolean>((resolve, reject) => {
      this.api.retrieve(URL.ALL_AVAILABLE_MODULES).then((data) => {
        this.availablePackages = this.fillArray(data);
        resolve(true);

      }).catch((error) => {
        console.log(error);
        reject(false);
      });
    });

    return promise;
  }

  public getAllInstalledPackages(): Promise<MagicMirrorPackage[]> {
    let promise = new Promise<MagicMirrorPackage[]>((resolve, reject) => {

      if (this.availablePackages?.length) resolve(this.availablePackages);

      this.api.retrieve(URL.ALL_INSTALLED_MODULES).then((data) => {
        this.installedPackages = this.fillArray(data);
        resolve(this.installedPackages);

      }).catch((error) => {
        console.log(error);
        reject(new Array<MagicMirrorPackage>());
      });
    });

    return promise;
  }

  public refreshAllInstalledPackages(): Promise<boolean> {
    let promise = new Promise<boolean>((resolve, reject) => {
      this.api.retrieve(URL.ALL_INSTALLED_MODULES).then((data) => {
        this.installedPackages = this.fillArray(data);
        resolve(true);
      }).catch((error) => {
        console.log(error);
        reject(false);
      });
    });

    return promise;
  }

  public getAllExternalPackages(): Promise<MagicMirrorPackage[]> {
    let promise = new Promise<MagicMirrorPackage[]>((resolve, reject) => {

      if (this.externalPackages?.length) resolve(this.externalPackages);

      this.api.retrieve(URL.ALL_EXTERNAL_MODULES).then((data) => {
        this.externalPackages = this.fillArray(data);
        resolve(this.externalPackages);
      }).catch((error) => {
        console.log(error);
        reject(new Array<MagicMirrorPackage>());
      });
    });

    return promise;
  }

  public refreshAllExternalPackages(): Promise<boolean> {
    let promise = new Promise<boolean>((resolve, reject) => {
      this.api.retrieve(URL.ALL_EXTERNAL_MODULES).then((data) => {
        this.externalPackages = this.fillArray(data);
        resolve(true);
      }).catch((error) => {
        console.log(error);
        reject(false);
      });
    });

    return promise;
  }
}
