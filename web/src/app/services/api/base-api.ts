import {HttpHeaders} from "@angular/common/http";

export interface APIResponse {
  code: number;
  message: any;
}

export class BaseAPI {
  constructor() {}

  public headers(options: object = {}): HttpHeaders {
    return new HttpHeaders({
      "Content-Type": "application/json",
      ...options,
    });
  }

  public route(path: string): string {
    return `http://${window.location.hostname}:7890/api/${path}`;
  }

  public handle_error(error: any): Promise<any> {
    const error_message = error.error instanceof ErrorEvent ? error.error.message : `Error Code: ${error.status}\nMessage: ${error.message}`;

    console.log(error_message);
    throw error_message;
  }

}
