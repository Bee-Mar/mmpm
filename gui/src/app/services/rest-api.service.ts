import { Injectable } from "@angular/core";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Observable, throwError } from "rxjs";
import { MagicMirrorPackage } from "src/app/interfaces/magic-mirror-package";
import { retry, catchError } from "rxjs/operators";
import { URL } from "src/app/utils/urls";

const httpOptions = (httpHeaders: object = {}) => {
  return new HttpHeaders({
    "Content-Type": "application/json",
    ...httpHeaders
  });
};

@Injectable({
  providedIn: "root"
})
export class RestApiService {
  constructor(private http: HttpClient) {}

  private route(path: string): string {
    return `http://${window.location.hostname}:7890/api${path}`;
  }

  public retrieve(path: string): Promise<any> {
    return this.http.get<any>(
      this.route(path), {
        headers: httpOptions()
      }).pipe(retry(1), catchError(this.handleError)).toPromise();
  }

  public refreshModules(): Observable<any> {
    return this.http.get<any>(
      this.route(URL.REFRESH_DATABASE),
      {
        headers: httpOptions()
      }).pipe(retry(1), catchError(this.handleError));
  }

  public getMagicMirrorConfig() {
    return this.http.get(
      this.route(URL.GET_MAGICMIRROR_CONFIG),
      {
        headers: httpOptions(),
        responseType: "text"
      });
  }

  private genericPost(url: string, selectedModules: MagicMirrorPackage[]): Promise<any> {
    return this.http.post(
      this.route(url),
      {
        "selected-modules": selectedModules
      },
      {
        headers: httpOptions({
          "Content-Type": "application/x-www-form-urlencoded"
        }),
        responseType: "text",
        reportProgress: true
      }).pipe(retry(1), catchError(this.handleError)).toPromise();
  }

  public installModules(selectedModules: MagicMirrorPackage[]): Promise<any> {
    return this.genericPost(URL.INSTALL_MODULES, selectedModules);
  }

  public upgradeModules(selectedModules: MagicMirrorPackage[]): Promise<any> {
    return this.genericPost(URL.UPGRADE_MODULES, selectedModules);
  }

  public uninstallModules(selectedModules: MagicMirrorPackage[]): Promise<any> {
    return this.genericPost(URL.UNINSTALL_MODULES, selectedModules);
  }

  public checkForInstallationConflicts(selectedModules: MagicMirrorPackage[]): Promise<any> {
    return this.genericPost(URL.CHECK_FOR_INSTALLATION_CONFLICT, selectedModules);
  }

  public updateMagicMirrorConfig(code: string): Observable<Response> {
    return this.http.post<any>(
      this.route(URL.UPDATE_MAGICMIRROR_CONFIG),
      {
        code
      },
      {
        headers: httpOptions({
          "Content-Type": "application/x-www-form-urlencoded"
        })
      }).pipe(retry(1), catchError(this.handleError));
  }

  public addExternalModuleSource(externalSource: MagicMirrorPackage): Observable<any> {
    return this.http.post<any>(
      this.route("/add-external-module-source"),
      {
        "external-source": externalSource
      },
      {
        headers: httpOptions({
          "Content-Type": "application/x-www-form-urlencoded"
        })
      }).pipe(retry(1), catchError(this.handleError));
  }

  public removeExternalModuleSource(externalSources: MagicMirrorPackage[]): Observable<any> {
    return this.http.request(
      "DELETE",
      this.route(URL.REMOVE_EXTERNAL_MODULE),
      {
        body: {
          "external-sources": externalSources
        },
        headers: httpOptions({
          "Content-Type": "text/plain"
        })
      }).pipe(retry(1), catchError(this.handleError));
  }

  public handleError(error: any) {
    const errorMessage = error.error instanceof ErrorEvent ?
      error.error.message :  `Error Code: ${error.status}\nMessage: ${error.message}`;

    window.alert(errorMessage);
    return throwError(errorMessage);
  }
}
