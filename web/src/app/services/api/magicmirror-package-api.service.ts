import {Injectable} from "@angular/core";
import {HttpClient} from "@angular/common/http";
import {MagicMirrorPackage} from "@/magicmirror/models/magicmirror-package";
import {APIResponse, BaseAPI} from '@/services/api/base-api';
import {retry, catchError} from "rxjs/operators";

@Injectable({
  providedIn: 'root'
})
export class MagicMirrorPackageAPI extends BaseAPI {
  constructor(private http: HttpClient) {
    super();
  }

  private post_packages(url: string, pkgs: MagicMirrorPackage[]): Promise<APIResponse> {
    return this.http
      .post(
        this.route(url),
        {
          "packages": pkgs,
        },
        {
          headers: this.options({
            "Content-Type": "application/x-www-form-urlencoded",
          }),
          responseType: "text",
          reportProgress: true,
        },
      )
      .pipe(retry(1), catchError(this.handle_error))
      .toPromise();
  }

  public get_retrieve_packages(): Promise<APIResponse> {
    return this.http
      .get(this.route("packages/retrieve"), {headers: this.options()})
      .pipe(retry(1), catchError(this.handle_error))
      .toPromise();
  }

  public post_install_packages(pkgs: MagicMirrorPackage[]): Promise<APIResponse> {
    return this.post_packages("packages/install", pkgs);
  }

  public post_remove_packages(pkgs: MagicMirrorPackage[]): Promise<APIResponse> {
    return this.post_packages("packages/remove", pkgs);
  }

  public post_upgrade_packages(pkgs: MagicMirrorPackage[]): Promise<APIResponse> {
    return this.post_packages("packages/upgrade", pkgs);
  }

  public post_add_mm_pkg(pkg: MagicMirrorPackage): Promise<APIResponse> {
    return this.post_packages("packages/mm-pkg/add", [pkg]);
  }

  public post_remove_mm_pkg(pkg: MagicMirrorPackage): Promise<APIResponse> {
    return this.post_packages("packages/mm-pkg/remove", [pkg]);
  }
}
