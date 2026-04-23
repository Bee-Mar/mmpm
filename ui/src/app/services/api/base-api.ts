import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { catchError, firstValueFrom, retry } from 'rxjs';

export interface APIResponse {
  code: number;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  message: any;
}

/*
 * if things get weird, removing the providedIn tag will probably resolve it so
 * this BaseAPI isn't a singleton, but it is right now
 */
@Injectable({
  providedIn: 'root',
})
export class BaseAPI {
  protected http = inject(HttpClient);

  public headers(options: object = {}): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      ...options,
    });
  }

  public route(path: string): string {
    const cfg = (window as unknown as Record<string, unknown>)['MMPM_CONFIG'] as { apiBase?: string } | undefined;
    return `${cfg?.apiBase ?? ''}/api/${path}`;
  }

  public get_(endpoint: string): Promise<APIResponse> {
    console.log(`Requesting data from ${endpoint}`);

    return firstValueFrom(
      this.http
        .get<APIResponse>(this.route(endpoint), { headers: this.headers() })
        .pipe(retry(1), catchError(this.handleError)),
    );
  }

  public getZipArchive(endpoint: string): Promise<ArrayBuffer> {
    return firstValueFrom(
      this.http
        .get(this.route(endpoint), {
          headers: this.headers({
            'Content-Type': 'application/zip',
          }),
          reportProgress: true,
          responseType: 'arraybuffer',
        })
        .pipe(retry(1), catchError(this.handleError)),
    );
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  public handleError(error: any): Promise<never> {
    const error_message =
      error.error instanceof ErrorEvent
        ? error.error.message
        : `Error Code: ${error.status}\nMessage: ${error.message}`;

    console.log(error_message);
    return Promise.reject(new Error(error_message));
  }
}
