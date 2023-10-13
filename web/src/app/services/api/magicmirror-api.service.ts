import {Injectable} from '@angular/core';
import {BaseAPI} from './base-api';
import {HttpClient} from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class MagicMirrorAPI extends BaseAPI {
  constructor(private http: HttpClient) {
    super();
  }
}
