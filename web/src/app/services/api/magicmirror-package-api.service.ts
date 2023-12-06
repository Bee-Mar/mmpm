import { Injectable } from "@angular/core";
import { MagicMirrorPackage } from "@/magicmirror/models/magicmirror-package";
import { APIResponse, BaseAPI } from "@/services/api/base-api";
import { retry, catchError, map } from "rxjs/operators";
import { firstValueFrom } from "rxjs";

@Injectable({
  providedIn: "root",
})
export class MagicMirrorPackageAPI extends BaseAPI {
  private post_packages(url: string, packages: MagicMirrorPackage[]): Promise<APIResponse> {
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
  public get_packages(): Promise<APIResponse> {
    console.log("Retrieving packages");
    return this.get_("packages");
  }

  public post_install_packages(packages: MagicMirrorPackage[]): Promise<APIResponse> {
    console.log("Requesting to have packages installed");
    return this.post_packages("packages/install", packages);
  }

  public post_remove_packages(packages: MagicMirrorPackage[]): Promise<APIResponse> {
    console.log("Requesting to have packages removed");
    return this.post_packages("packages/remove", packages);
  }

  public post_upgrade_packages(packages: MagicMirrorPackage[]): Promise<APIResponse> {
    console.log("Requesting to have packages upgraded");
    return this.post_packages("packages/upgrade", packages);
  }

  public post_add_mm_pkg(pkg: MagicMirrorPackage): Promise<APIResponse> {
    console.log("Requesting to add a custom MagicMirrorPackage");
    return this.post_packages("packages/mm-pkg/add", [pkg]);
  }

  public post_remove_mm_pkg(pkg: MagicMirrorPackage): Promise<APIResponse> {
    console.log("Requesting to remove a custom MagicMirrorPackage");
    return this.post_packages("packages/mm-pkg/remove", [pkg]);
  }
  public post_details(pkg: MagicMirrorPackage): Promise<APIResponse> {
    console.log(`Requesting to get remote package details for ${pkg.title} (${pkg.repository})`);
    return this.post_packages("packages/details", [pkg]);
  }
}
