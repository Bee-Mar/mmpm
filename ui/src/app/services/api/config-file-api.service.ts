import { Injectable } from "@angular/core";
import { APIResponse, BaseAPI } from "./base-api";
import { catchError, firstValueFrom, retry } from "rxjs";

@Injectable({
  providedIn: "root",
})
export class ConfigFileAPI extends BaseAPI {
  public getConfigFile(filename: string): Promise<string> {
    console.log(`Retrieving ${filename}`);

    return firstValueFrom(
      this.http
        .get(this.route(`configs/retrieve/${filename}`), {
          headers: this.headers(),
          responseType: "text",
        })
        .pipe(retry(1), catchError(this.handleError)),
    );
  }

  public postConfigFile(filename: string, contents: string): Promise<APIResponse> {
    console.log(`Updating ${filename}`);

    return firstValueFrom(
      this.http
        .post<string>(
          this.route(`configs/update/${filename}`),
          {
            contents,
          },
          {
            headers: this.headers({
              "Content-Type": "application/json",
            }),
          },
        )
        .pipe(retry(1), catchError(this.handleError)),
    );
  }
}
