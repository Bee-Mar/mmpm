import { Injectable } from "@angular/core";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";
import { RestApiService } from "src/app/services/rest-api.service";
import { URLS } from "src/app/utils/urls";

@Injectable({
  providedIn: "root"
})
export class DataStoreService {
  private availablePackages: MagicMirrorPackage[];
  private installedPackages: MagicMirrorPackage[];
  private externalPackages: MagicMirrorPackage[];
  private availableUpgrades: Object;
  private magicmirrorRootDirectory: string = "";

  constructor(private api: RestApiService) {}

  public ngOnInit(): void {
    this.availablePackages = new Array<MagicMirrorPackage>();
    this.installedPackages = new Array<MagicMirrorPackage>();
    this.externalPackages = new Array<MagicMirrorPackage>();
    this.availableUpgrades = new Object();

    this.getAllAvailablePackages(true);
    this.getAllInstalledPackages(true);
    this.getAllExternalPackages(true);
    this.getMagicMirrorRootDirectory(true);
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
            directory: pkg["directory"]
          });
        }
      }
    });

    return array;
  }

  public getAllAvailablePackages(refresh: boolean = false): Promise<MagicMirrorPackage[]> {
    let promise = new Promise<MagicMirrorPackage[]>((resolve, reject) => {

      if (this.availablePackages?.length && !refresh) {
        resolve(this.availablePackages);

      } else {
        this.api.retrieve(URLS.GET.PACKAGES.MARKETPLACE).then((data) => {
          this.availablePackages = this.fillArray(data);
          resolve(this.availablePackages);

        }).catch((error) => {
          console.log(error);
          reject(new Array<MagicMirrorPackage>());
        });
      }
    });

    return promise;
  }

  public getAllInstalledPackages(refresh: boolean = false): Promise<MagicMirrorPackage[]> {
    let promise = new Promise<MagicMirrorPackage[]>((resolve, reject) => {

      if (this.installedPackages?.length && !refresh) {
        resolve(this.installedPackages);

      } else {
        this.api.retrieve(URLS.GET.PACKAGES.INSTALLED).then((data) => {
          this.installedPackages = this.fillArray(data);
          resolve(this.installedPackages);

        }).catch((error) => {
          console.log(error);
          reject(new Array<MagicMirrorPackage>());
        });
      }
    });

    return promise;
  }

  public getAllExternalPackages(refresh: boolean = false): Promise<MagicMirrorPackage[]> {
    let promise = new Promise<MagicMirrorPackage[]>((resolve, reject) => {

      if (this.externalPackages?.length && !refresh) {
        resolve(this.externalPackages);

      } else {
        this.api.retrieve(URLS.GET.PACKAGES.EXTERNAL).then((data) => {
          this.externalPackages = this.fillArray(data);
          resolve(this.externalPackages);

        }).catch((error) => {
          console.log(error);
          reject(new Array<MagicMirrorPackage>());
        });
      }
    });

    return promise;
  }

  public getAvailableUpgrades(refresh: boolean = false): Promise<object> {
    let promise = new Promise<object>((resolve, reject) => {
      if (this.availableUpgrades && !refresh) {
        resolve(this.availableUpgrades);

      } else {
        this.api.retrieve(URLS.GET.PACKAGES.UPGRADEABLE).then((data) => {
          this.availableUpgrades = data;
          resolve(this.availableUpgrades);

        }).catch((error) => {
          console.log(error);
          reject(new Object());

        });
      }
    });

    return promise;
  }

  public getMagicMirrorRootDirectory(refresh: boolean = false): Promise<string> {
    let promise = new Promise<string>((resolve, reject) => {
      if (this.magicmirrorRootDirectory.length && !refresh) {
        resolve(this.magicmirrorRootDirectory);

      } else {
        this.api.retrieve(URLS.GET.MAGICMIRROR.ROOT_DIR).then((url: object) => {
          this.magicmirrorRootDirectory = url["magicmirror_root"];

        }).catch((error) => {
          console.log(error);
          reject("");

        });
      }
    });

    return promise;
  }

}
