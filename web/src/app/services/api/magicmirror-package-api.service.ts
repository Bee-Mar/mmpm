import { Injectable } from "@angular/core";
import { MagicMirrorPackage } from "@/models/magicmirror-package";
import { APIResponse, BaseAPI } from "@/services/api/base-api";
import { retry, catchError, map } from "rxjs/operators";
import { firstValueFrom } from "rxjs";

@Injectable({
  providedIn: "root",
})
export class MagicMirrorPackageAPI extends BaseAPI {
  private postPackages(url: string, packages: MagicMirrorPackage[]): Promise<APIResponse> {
    return firstValueFrom(
      this.http.post(this.route(url), { packages }, { headers: this.headers({ "Content-Type": "application/json" }) }).pipe(
        map((response) => {
          return typeof response === "string" ? JSON.parse(response) : response;
        }),
        retry(1),
        catchError(this.handle_error),
      ),
    );
  }

  private postPackage(url: string, pkg: MagicMirrorPackage): Promise<APIResponse> {
    return firstValueFrom(
      this.http.post(this.route(url), { package: pkg }, { headers: this.headers({ "Content-Type": "application/json" }) }).pipe(
        map((response) => {
          return typeof response === "string" ? JSON.parse(response) : response;
        }),
        retry(1),
        catchError(this.handle_error),
      ),
    );
  }
  public getPackages(): Promise<APIResponse> {
    console.log("Retrieving packages from API");
    return this.get_("packages");
  }

  public postInstallPackages(packages: MagicMirrorPackage[]): Promise<APIResponse> {
    console.log(`Requesting to have ${packages.length} packages installed`);
    return this.postPackages("packages/install", packages);
  }

  public postRemovePackages(packages: MagicMirrorPackage[]): Promise<APIResponse> {
    console.log(`Requesting to have ${packages.length} packages removed`);
    return this.postPackages("packages/remove", packages);
  }

  public postUpgradePackages(packages: MagicMirrorPackage[]): Promise<APIResponse> {
    console.log("Requesting to have packages upgraded");
    return this.postPackages("packages/upgrade", packages);
  }

  public postAddMmPkg(pkg: MagicMirrorPackage): Promise<APIResponse> {
    console.log("Requesting to add a custom MagicMirrorPackage");
    return this.postPackage("packages/mm-pkg/add", pkg);
  }

  public postRemoveMmPkgs(packages: MagicMirrorPackage[]): Promise<APIResponse> {
    console.log("Requesting to remove a custom MagicMirrorPackage");
    return this.postPackages("packages/mm-pkg/remove", packages);
  }
  public postDetails(pkg: MagicMirrorPackage): Promise<APIResponse> {
    console.log(`Requesting to get remote package details for ${pkg.title} (${pkg.repository})`);
    return this.postPackages("packages/details", [pkg]);
  }
}
