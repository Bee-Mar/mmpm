import { Injectable } from "@angular/core";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Observable, throwError } from "rxjs";
import { MagicMirrorPackage } from "src/app/interfaces/magic-mirror-package";
import { retry, catchError } from "rxjs/operators";

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
  private BASE_API_URL = `http://${window.location.hostname}:7890/api`;

  constructor(private http: HttpClient) {}

  public retrieve(path: string): Observable<any> {
    return this.http.get<any>(
      this.BASE_API_URL + `${path}`,
      {
        headers: httpOptions()
      }).pipe(retry(1), catchError(this.handleError));
  }

  public refreshModules(): Observable<any> {
    return this.http.get<any>(
      this.BASE_API_URL + "/refresh-modules",
      {
        headers: httpOptions()
      }).pipe(retry(1), catchError(this.handleError));
  }

  public getMagicMirrorConfig() {
    return this.http.get(
      this.BASE_API_URL + "/get-magicmirror-config",
      {
        headers: httpOptions(),
        responseType: "text"
    });
  }

  private genericPost(url: string, selectedModules: MagicMirrorPackage[]): Observable<any> {
    return this.http.post(
        this.BASE_API_URL + url,
        {
          "selected-modules": selectedModules
        },
        {
          headers: httpOptions({
            "Content-Type": "application/x-www-form-urlencoded"
          }),
          responseType: "text",
          reportProgress: true
        }).pipe(retry(1), catchError(this.handleError));
  }

  public installModules(selectedModules: MagicMirrorPackage[]): Observable<any> {
    return this.genericPost("/install-modules", selectedModules);
  }

  public upgradeModules(selectedModules: MagicMirrorPackage[]): Observable<any> {
    return this.genericPost("/upgrade-modules", selectedModules);
  }

  public uninstallModules(selectedModules: MagicMirrorPackage[]): Observable<any> {
    return this.genericPost("/uninstall-modules", selectedModules);
  }

  public updateMagicMirrorConfig(code: string): Observable<Response> {
    return this.http.post<any>(
        this.BASE_API_URL + "/update-magicmirror-config",
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
        this.BASE_API_URL + "/add-external-module-source",
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
      this.BASE_API_URL + "/remove-external-module-source",
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
