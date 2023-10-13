import {Component, OnInit} from '@angular/core';
import {MagicMirrorPackage} from "@/magicmirror/models/magicmirror-package";
import {SharedStoreService} from '@/services/shared-store.service';
import {MagicMirrorPackageAPI} from '@/services/api/magicmirror-package-api.service';

@Component({
  selector: 'app-magicmirror-database',
  templateUrl: './magicmirror-database.component.html',
  styleUrls: ['./magicmirror-database.component.scss']
})
export class MagicMirrorDatabaseComponent implements OnInit {

  constructor(private store: SharedStoreService, private mm_pkg_api: MagicMirrorPackageAPI) {}

  public packages: Array<MagicMirrorPackage> = new Array<MagicMirrorPackage>();

  ngOnInit(): void {
    this.store.packages.subscribe(packages => this.packages = packages);
  }

  public info() {

  }

  public install(pkgs: MagicMirrorPackage[]) {
    this.mm_pkg_api.post_install_packages(pkgs).then(_ => {
      this.store.retrieve_packages();
    });
  }

  public remove(pkgs: MagicMirrorPackage[]) {
    this.mm_pkg_api.post_remove_packages(pkgs).then(_ => {
      this.store.retrieve_packages();
    });
  }

  public upgrade(pkgs: MagicMirrorPackage[]) {
    this.mm_pkg_api.post_upgrade_packages(pkgs).then(_ => {
      this.store.retrieve_packages();
    });
  }

  public add_mm_pkg(pkg: MagicMirrorPackage) {
    this.mm_pkg_api.post_add_mm_pkg(pkg).then(_ => {
      this.store.retrieve_packages();
    });
  }

  public remove_mm_pkg(pkg: MagicMirrorPackage) {
    this.mm_pkg_api.post_add_mm_pkg(pkg).then(_ => {
      this.store.retrieve_packages();
    });
  }


}
