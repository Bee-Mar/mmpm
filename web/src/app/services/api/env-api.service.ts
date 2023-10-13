import {Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {APIResponse, BaseAPI} from './base-api';

@Injectable({
  providedIn: 'root'
})
export class EnvAPI extends BaseAPI {
  constructor(private http: HttpClient) {
    super();
  }

  //public get_retrieve_env(): Promise<APIResponse> {

  //}
}
