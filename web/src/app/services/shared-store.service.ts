import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from "rxjs";
import { MagicMirrorPackage } from "@/magicmirror/models/magicmirror-package"
import { MagicMirrorPackageAPI } from './api/magicmirror-package-api.service';
import { APIResponse } from '@/services/api/base-api';

@Injectable({
  providedIn: 'root'
})
export class SharedStoreService {

  constructor(private _mm_pkg_api: MagicMirrorPackageAPI) { }

  private _packages: BehaviorSubject<MagicMirrorPackage[]> = new BehaviorSubject<Array<MagicMirrorPackage>>([]);
  public readonly packages: Observable<MagicMirrorPackage[]> = this._packages.asObservable();

  public retrieve_packages(): void {
    this._mm_pkg_api.get_retrieve_packages().then((response: APIResponse) => this._packages.next(JSON.parse(response.message)));
  }

}
