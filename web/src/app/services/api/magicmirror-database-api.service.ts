import {Injectable} from '@angular/core';
import {APIResponse, BaseAPI} from './base-api';
import {HttpClient} from "@angular/common/http";

@Injectable({
  providedIn: 'root'
})
export class MagicMirrorDatabaseAPI extends BaseAPI {
  constructor(private http: HttpClient) {
    super();
  }

  public get_upgradeable(): Promise<APIResponse> {
    return this.http.get(this.route("database/upgradeable")).pipe(retry(1), catchError(this.handle_error)).toPromise();
  }

}
