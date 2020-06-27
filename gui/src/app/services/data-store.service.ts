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

  constructor(private api: RestApiService) {}

  public ngOnInit(): void {
    this.availablePackages = new Array<MagicMirrorPackage>();
    this.installedPackages = new Array<MagicMirrorPackage>();
    this.externalPackages = new Array<MagicMirrorPackage>();

    this.getAllAvailablePackages();
    this.getAllInstalledPackages();
    this.getAllExternalPackages();
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
}
