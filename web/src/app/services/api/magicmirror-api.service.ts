import {Injectable} from '@angular/core';
import {APIResponse, BaseAPI} from './base-api';

@Injectable({
  providedIn: 'root'
})
export class MagicMirrorAPI extends BaseAPI {
  public get_status(): Promise<APIResponse> {
    return this.get_("mm");

  }
}
