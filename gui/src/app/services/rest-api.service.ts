import { Injectable } from "@angular/core";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Observable, throwError } from "rxjs";
import { MagicMirrorPackage } from "src/app/interfaces/magic-mirror-package";
import { retry, catchError } from "rxjs/operators";

const httpOptions = (httpHeaders: object = {}) => {
  return {
    headers: new HttpHeaders({
      "Content-Type": "application/json",
      ...httpHeaders
    })
  };
};

@Injectable({
  providedIn: "root"
})
export class RestApiService {
  BASE_API_URL = "http://0.0.0.0:7891/api";

  constructor(private http: HttpClient) {}

  public mmpmApiRequest(path: string): Observable<any> {
    return this.http
      .get<any>(this.BASE_API_URL + `${path}`, httpOptions())
      .pipe(retry(1), catchError(this.handleError));
  }

  public getMagicMirrorConfig() {
    return this.http.get(this.BASE_API_URL + "/get-magicmirror-config", {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json"
      },
      responseType: "text"
    });
  }

  public installSelectedModules(selectedModules: any): Observable<any> {
    return this.http
      .post(
        this.BASE_API_URL + "/install-modules",
        httpOptions({ "Content-Type": "text/plain" })
      )
      .pipe(retry(1), catchError(this.handleError));
  }

  public updateMagicMirrorConfig(code: string): Observable<Response> {
    return this.http
      .post<any>(
        this.BASE_API_URL + "/update-magicmirror-config",
        { code },
        httpOptions({ "Content-Type": "application/x-www-form-urlencoded" })
      )
      .pipe(retry(1), catchError(this.handleError));
  }

  public registerExternalModuleSource(externalSource: MagicMirrorPackage): Observable<any> {
    return this.http
      .post<any>(
        this.BASE_API_URL + "/register-external-module-source",
        { "external-source": externalSource },
        httpOptions({ "Content-Type": "application/x-www-form-urlencoded" })
      )
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
