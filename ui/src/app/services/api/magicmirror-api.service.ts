import { Injectable } from "@angular/core";
import { APIResponse, BaseAPI } from "./base-api";

@Injectable({
  providedIn: "root",
})
export class MagicMirrorAPI extends BaseAPI {
  public getStatus(): Promise<APIResponse> {
    console.log("Requesting MagicMirror module statuses");
    return this.get_("mm-ctl/status");
  }

  public getUpgrade(): Promise<APIResponse> {
    console.log("Requesting MagicMirror perform upgrade");
    return this.get_("mm-ctl/upgrade");
  }

  public getInstall(): Promise<APIResponse> {
    console.log("Requesting MagicMirror perform upgrade");
    return this.get_("mm-ctl/install");
  }

  public getRemove(): Promise<APIResponse> {
    console.log("Requesting MagicMirror perform upgrade");
    return this.get_("mm-ctl/remove");
  }
}
