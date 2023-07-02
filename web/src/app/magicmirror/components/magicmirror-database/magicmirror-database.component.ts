import { Component, OnInit } from '@angular/core';
import { MagicMirrorPackage } from "@/magicmirror/models/magicmirror-package"
import { SharedStoreService } from '@/services/shared-store.service';
import { RestApiService } from '@/services/rest-api-service.service';

@Component({
  selector: 'app-magicmirror-database',
  templateUrl: './magicmirror-database.component.html',
  styleUrls: ['./magicmirror-database.component.scss']
})
export class MagicMirrorDatabaseComponent implements OnInit {

  constructor(private _store: SharedStoreService, private _api: RestApiService) { }

  public packages: Array<MagicMirrorPackage> = new Array<MagicMirrorPackage>();

  ngOnInit(): void {
    this._store.packages.subscribe(packages => this.packages = packages);
  }

  public info() {

  }

  public install(pkgs: MagicMirrorPackage[]) {
    this._api.post_install_packages(pkgs).then(_ => {
      this._store.retrieve_packages();
    });
  }

  public remove(pkgs: MagicMirrorPackage[]) {
    this._api.post_remove_packages(pkgs).then(_ => {
      this._store.retrieve_packages();
    });
  }

  public upgrade(pkgs: MagicMirrorPackage[]) {
    this._api.post_upgrade_packages(pkgs).then(_ => {
      this._store.retrieve_packages();
    });
  }

  public add_mm_pkg(pkg: MagicMirrorPackage) {
    this._api.post_add_mm_pkg(pkg).then(_ => {
      this._store.retrieve_packages();
    });
  }

  public remove_mm_pkg(pkg: MagicMirrorPackage) {
    this._api.post_add_mm_pkg(pkg).then(_ => {
      this._store.retrieve_packages();
    });
  }


}
