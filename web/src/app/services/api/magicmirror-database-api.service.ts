import {Injectable} from '@angular/core';
import {APIResponse, BaseAPI} from './base-api';
import {HttpClient} from "@angular/common/http";
import {firstValueFrom} from 'rxjs';
import {retry, catchError} from "rxjs/operators";

@Injectable({
  providedIn: 'root'
})
export class MagicMirrorDatabaseAPI extends BaseAPI {
  constructor(private http: HttpClient) {
    super();
  }

  public load(): Promise<APIResponse> {
    return firstValueFrom(
      this.http
        .get<APIResponse>(this.route("db/load"), {headers: this.options()})
        .pipe(retry(1), catchError(this.handle_error))
    );
  }

  public get_upgradeable(): Promise<APIResponse> {
    return this.http.get(this.route("db/upgradeable")).pipe(retry(1), catchError(this.handle_error)).toPromise();
  }

}
