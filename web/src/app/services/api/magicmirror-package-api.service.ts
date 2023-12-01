import {Injectable} from "@angular/core";
import {HttpClient} from "@angular/common/http";
import {MagicMirrorPackage} from "@/magicmirror/models/magicmirror-package";
import {APIResponse, BaseAPI} from '@/services/api/base-api';
import {retry, catchError} from "rxjs/operators";
import {firstValueFrom} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MagicMirrorPackageAPI extends BaseAPI {
  constructor(private http: HttpClient) {
    super();
  }

  private post_packages(url: string, packages: MagicMirrorPackage[]): Promise<APIResponse> {
    return firstValueFrom(
      this.http
        .post(
          this.route(url),
          {
            packages,
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
    );
  }

  public get_packages(): Promise<APIResponse> {
    return firstValueFrom(
      this.http
        .get<APIResponse>(this.route("packages"), {headers: this.options()})
        .pipe(retry(1), catchError(this.handle_error))
    );
  }

  public post_install_packages(packages: MagicMirrorPackage[]): Promise<APIResponse> {
    return this.post_packages("packages/install", packages);
  }

  public post_remove_packages(packages: MagicMirrorPackage[]): Promise<APIResponse> {
    return this.post_packages("packages/remove", packages);
  }

  public post_upgrade_packages(packages: MagicMirrorPackage[]): Promise<APIResponse> {
    return this.post_packages("packages/upgrade", packages);
  }

  public post_add_mm_pkg(pkg: MagicMirrorPackage): Promise<APIResponse> {
    return this.post_packages("packages/mm-pkg/add", [pkg]);
  }

  public post_remove_mm_pkg(pkg: MagicMirrorPackage): Promise<APIResponse> {
    return this.post_packages("packages/mm-pkg/remove", [pkg]);
  }
}
