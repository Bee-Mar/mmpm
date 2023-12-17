import {Injectable} from "@angular/core";
import {APIResponse, BaseAPI} from "./base-api";
import {MagicMirrorModule} from '@/models/magicmirror-module';
import {catchError, firstValueFrom, map, retry} from 'rxjs';

@Injectable({
  providedIn: "root",
})
export class MagicMirrorControllerAPI extends BaseAPI {
  public getStart(): Promise<APIResponse> {
    console.log("Requesting to start MagicMirror");
    return this.get_("mm-ctl/start");
  }

  public getRestart(): Promise<APIResponse> {
    console.log("Requesting to restart MagicMirror");
    return this.get_("mm-ctl/restart");
  }

  public getStop(): Promise<APIResponse> {
    console.log("Requesting to stop MagicMirror");
    return this.get_("mm-ctl/stop");
  }

  public postHide(mmModule: MagicMirrorModule): Promise<APIResponse> {
    return this.postModule("mm-ctl/hide", mmModule);
  }

  public postShow(mmModule: MagicMirrorModule): Promise<APIResponse> {
    return this.postModule("mm-ctl/show", mmModule);
  }

  private postModule(url: string, mmModule: MagicMirrorModule): Promise<APIResponse> {
    return firstValueFrom(
      this.http.post(this.route(url), {"module": [String(mmModule.key)]}, {headers: this.headers({"Content-Type": "application/json"})}).pipe(
        map((response) => {
          return typeof response === "string" ? JSON.parse(response) : response;
        }),
        retry(1),
        catchError(this.handle_error),
      ),
    );
  }
}
