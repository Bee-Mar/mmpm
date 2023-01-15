import { Injectable } from "@angular/core";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Observable, throwError } from "rxjs";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";
import { retry, catchError } from "rxjs/operators";
import { URLS } from "src/app/utils/urls";

const httpOptions = (httpHeaders: object = {}) =>
  new HttpHeaders({
    "Content-Type": "application/json",
    ...httpHeaders,
  });

@Injectable({
  providedIn: "root",
})
export class RestApiService {
  constructor(private http: HttpClient) {}

  private route(path: string): string {
    return `http://${window.location.hostname}:7890/api${path}`;
  }

  public retrieve(path: string): Promise<any> {
    return this.http
      .get<any>(this.route(path), {
        headers: httpOptions(),
      })
      .pipe(retry(1), catchError(this.handleError))
      .toPromise();
  }

  public getFile(url: string): Promise<any> {
    return this.http
      .get(this.route(url), {
        headers: httpOptions(),
        responseType: "text",
      })
      .pipe(retry(1), catchError(this.handleError))
      .toPromise();
  }

  private postWithSelectedPackages(url: string, selectedPackages: MagicMirrorPackage[]): Promise<any> {
    return this.http
      .post(
        this.route(url),
        {
          "selected-packages": selectedPackages,
        },
        {
          headers: httpOptions({
            "Content-Type": "application/x-www-form-urlencoded",
          }),
          responseType: "text",
          reportProgress: true,
        },
      )
      .pipe(retry(1), catchError(this.handleError))
      .toPromise();
  }

  public packagesInstall(selectedPackages: MagicMirrorPackage[]): Promise<any> {
    return this.postWithSelectedPackages(URLS.POST.PACKAGES.INSTALL, selectedPackages);
  }

  public packagesUpgrade(selectedPackages: MagicMirrorPackage[]): Promise<any> {
    return this.postWithSelectedPackages(URLS.POST.PACKAGES.UPGRADE, selectedPackages);
  }

  public packagesRemove(selectedPackages: MagicMirrorPackage[]): Promise<any> {
    return this.postWithSelectedPackages(URLS.POST.PACKAGES.REMOVE, selectedPackages);
  }

  public getLogFiles(): Promise<any> {
    return this.http
      .get(this.route(URLS.GET.MMPM.DOWNLOAD_LOGS), {
        headers: httpOptions({
          "Content-Type": "application/zip",
        }),
        reportProgress: true,
        responseType: "arraybuffer",
      })
      .pipe(retry(1), catchError(this.handleError))
      .toPromise();
  }

  public updateMagicMirrorConfig(url: string, code: string): Observable<Response> {
    return this.http
      .post<any>(
        this.route(url),
        {
          code,
        },
        {
          headers: httpOptions({
            "Content-Type": "application/x-www-form-urlencoded",
          }),
        },
      )
      .pipe(retry(1), catchError(this.handleError));
  }

  public addExternalPackage(externalSource: MagicMirrorPackage): Promise<any> {
    return this.http
      .post<any>(
        this.route(URLS.POST.EXTERNAL_PACKAGES.ADD),
        {
          "external-package": externalSource,
        },
        {
          headers: httpOptions({
            "Content-Type": "application/x-www-form-urlencoded",
          }),
        },
      )
      .pipe(retry(1), catchError(this.handleError))
      .toPromise();
  }

  public rotateRaspberryPiScreen(degrees: number): Promise<boolean> {
    return this.http
      .post<boolean>(
        this.route(URLS.POST.RASPBERRYPI.ROTATE_SCREEN),
        {
          degrees: String(degrees),
        },
        {
          headers: httpOptions({
            "Content-Type": "application/x-www-form-urlencoded",
          }),
        },
      )
      .pipe(retry(1), catchError(this.handleError))
      .toPromise();
  }

  public removeExternalPackage(externalSources: MagicMirrorPackage[]): Promise<any> {
    return this.http
      .request("DELETE", this.route(URLS.DELETE.EXTERNAL_PACKAGES.REMOVE), {
        body: {
          "external-packages": externalSources,
        },
        headers: httpOptions({
          "Content-Type": "text/plain",
        }),
      })
      .pipe(retry(1), catchError(this.handleError))
      .toPromise();
  }

  public upgradeMagicMirror(): Promise<any> {
    return this.retrieve(URLS.GET.MAGICMIRROR.UPGRADE);
  }

  public handleError(error: any): Promise<any> {
    const errorMessage = error.error instanceof ErrorEvent ? error.error.message : `Error Code: ${error.status}\nMessage: ${error.message}`;

    // window.alert(errorMessage);
    console.log(errorMessage);
    return throwError(errorMessage).toPromise();
  }
}
