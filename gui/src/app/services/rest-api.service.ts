import { Injectable } from "@angular/core";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Observable, throwError } from "rxjs";
import { MagicMirrorPackage } from "src/app/classes/magic-mirror-package";
import { retry, catchError } from "rxjs/operators";

@Injectable({
  providedIn: "root"
})
export class RestApiService {
  MMPM_API_URL = "http://0.0.0.0:8090/api";

  constructor(private http: HttpClient) {}

  public httpOptions = {
    headers: new HttpHeaders({
      "Access-Control-Allow-Origin": "*",
      "Content-Type": "application/json"
    })
  };

  public mmpmApiRequest(path: string): Observable<any> {
    return this.http
      .get<any>(this.MMPM_API_URL + `${path}`, this.httpOptions)
      .pipe(retry(1), catchError(this.handleError));
  }

  public getMagicMirrorConfig() {
    return this.http.get(this.MMPM_API_URL + "/get-magicmirror-config", {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json"
      },
      responseType: "text"
    });
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
