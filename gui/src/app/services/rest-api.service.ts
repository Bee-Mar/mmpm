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
  private BASE_API_URL = "http://127.0.0.1:7891/api";

  constructor(private http: HttpClient) {}

  public getModules(path: string): Observable<any> {
    return this.http.get<any>(this.BASE_API_URL + `${path}`, { headers: httpOptions() }).pipe(retry(1), catchError(this.handleError));
  }

  public getMagicMirrorConfig() {
    return this.http.get(this.BASE_API_URL + "/get-magicmirror-config", {
      headers: httpOptions(),
      responseType: "text"
    });
  }

  public modifyModules(url: string, selectedModules: MagicMirrorPackage[]): Observable<any> {
    return this.http.post(
        this.BASE_API_URL + url,
        {
          "selected-modules": selectedModules
        },
        {
          headers: httpOptions({"Content-Type": "application/x-www-form-urlencoded"}),
          responseType: "text",
          reportProgress: true
        }
      )
      .pipe(retry(1), catchError(this.handleError));
  }

  public updateMagicMirrorConfig(code: string): Observable<Response> {
    return this.http.post<any>(
        this.BASE_API_URL + "/update-magicmirror-config",
        {
          code
        },
        {
          headers: httpOptions({"Content-Type": "application/x-www-form-urlencoded"})
        }
      )
      .pipe(retry(1), catchError(this.handleError));
  }

  public addExternalModuleSource(externalSource: MagicMirrorPackage): Observable<any> {
    return this.http.post<any>(
        this.BASE_API_URL + "/add-external-module-source",
        {
          "external-source": externalSource
        },
        {
          headers: httpOptions({"Content-Type": "application/x-www-form-urlencoded"})
        }
      )
      .pipe(retry(1), catchError(this.handleError));
  }

  public updateModules(selectedModules: MagicMirrorPackage[]): Observable<any> {
    return this.http.post<any>(
        this.BASE_API_URL + "/update-modules",
        {
          "selected-modules": selectedModules
        },
        {
          headers: httpOptions({
            "Content-Type": "application/x-www-form-urlencoded"
          })
        }
      )
      .pipe(retry(1), catchError(this.handleError));
  }

  public removeExternalModuleSource(externalSources: MagicMirrorPackage[]): Observable<any> {
    return this.http.request("DELETE", this.BASE_API_URL + "/remove-external-module-source", {
        body: {
          "external-sources": externalSources
        },
        headers: httpOptions({ "Content-Type": "text/plain" })
      })
      .pipe(retry(1), catchError(this.handleError));
  }

  public handleError(error: any) {
    let errorMessage = "";

    if (error.error instanceof ErrorEvent) {
      errorMessage = error.error.message;
    } else {
      errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
    }

    window.alert(errorMessage);
    return throwError(errorMessage);
  }
}
