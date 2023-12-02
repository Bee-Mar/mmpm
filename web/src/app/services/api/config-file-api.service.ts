import {Injectable} from '@angular/core';
import {APIResponse, BaseAPI} from './base-api';
import {HttpClient} from '@angular/common/http';
import {catchError, firstValueFrom, retry} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ConfigFileAPI extends BaseAPI {

  constructor(private http: HttpClient) {
    super();
  }

  public get_config_file(filename: string): Promise<string> {
    console.log(`Retrieving ${filename}`);

    return firstValueFrom(
      this.http
        .get(this.route(`configs/retrieve/${filename}`), {
          headers: this.headers(),
          responseType: "text",
        })
        .pipe(retry(1), catchError(this.handle_error))
    );
  }

  public post_config_file(filename: string, contents: string): Promise<string> {
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
              "Content-Type": "application/x-www-form-urlencoded",
            }),
          },
        )
        .pipe(retry(1), catchError(this.handle_error)));
  }
}
