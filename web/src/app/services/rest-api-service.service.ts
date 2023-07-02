import { Injectable } from "@angular/core";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { throwError } from "rxjs";
import { MagicMirrorPackage } from "@/magicmirror/models/magicmirror-package";
import { retry, catchError } from "rxjs/operators";

interface Response {
  code: number;
  message: any;
}

const options = (headers: object = {}) =>
  new HttpHeaders({
    "Content-Type": "application/json",
    ...headers,
  });

@Injectable({
  providedIn: 'root'
})
export class RestApiService {
  constructor(private _http: HttpClient) { }

  private route(path: string): string {
    return `http://${window.location.hostname}:7890/api/${path}`;
  }

  private handle_error(error: any): Promise<any> {
    const error_message = error.error instanceof ErrorEvent ? error.error.message : `Error Code: ${error.status}\nMessage: ${error.message}`;

    console.log(error_message);
    return throwError(error_message).toPromise();
  }

  public get_retrieve_packages(): Promise<Response> {
    return this._http
      .get(this.route("packages/retrieve"), { headers: options() })
      .pipe(retry(1), catchError(this.handle_error))
      .toPromise();
  }

  private _post_packages(url: string, pkgs: MagicMirrorPackage[]): Promise<Response> {
    return this._http
      .post(
        this.route(url),
        {
          "packages": pkgs,
        },
        {
          headers: options({
            "Content-Type": "application/x-www-form-urlencoded",
          }),
          responseType: "text",
          reportProgress: true,
        },
      )
      .pipe(retry(1), catchError(this.handle_error))
      .toPromise();
  }

  public post_install_packages(pkgs: MagicMirrorPackage[]): Promise<Response> {
    return this._post_packages("packages/install", pkgs);
  }

  public post_remove_packages(pkgs: MagicMirrorPackage[]): Promise<Response> {
    return this._post_packages("packages/remove", pkgs);
  }

  public post_upgrade_packages(pkgs: MagicMirrorPackage[]): Promise<Response> {
    return this._post_packages("packages/upgrade", pkgs);
  }

  public post_add_mm_pkg(pkg: MagicMirrorPackage): Promise<Response> {
    return this._post_packages("packages/mm-pkg/add", [pkg]);
  }

  public post_remove_mm_pkg(pkg: MagicMirrorPackage): Promise<Response> {
    return this._post_packages("packages/mm-pkg/remove", [pkg]);
  }

  public get_database_info(): Promise<Response> {
    return this._http
      .get(this.route("database/info"), { headers: options() })
      .pipe(retry(1), catchError(this.handle_error))
      .toPromise();
  }
}
