import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from "rxjs";
import { MagicMirrorPackage } from "@/magicmirror/models/magicmirror-package"
import { RestApiService } from "@/services/rest-api-service.service"

@Injectable({
  providedIn: 'root'
})
export class SharedStoreService {

  constructor(private _api: RestApiService) { }

  private _packages: BehaviorSubject<MagicMirrorPackage[]> = new BehaviorSubject<Array<MagicMirrorPackage>>([]);
  public readonly packages: Observable<MagicMirrorPackage[]> = this._packages.asObservable();

  public retrieve_packages(): void {
    this._api.get_retrieve_packages().then(response => this._packages.next(JSON.parse(response.message)));
  }

}
