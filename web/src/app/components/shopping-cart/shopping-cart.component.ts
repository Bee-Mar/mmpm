import { MagicMirrorPackage } from "@/models/magicmirror-package";
import { MagicMirrorPackageAPI } from "@/services/api/magicmirror-package-api.service";
import { SharedStoreService } from "@/services/shared-store.service";
import { Component, Input, Output, EventEmitter } from "@angular/core";

@Component({
  selector: "app-shopping-cart",
  templateUrl: "./shopping-cart.component.html",
  styleUrls: ["./shopping-cart.component.scss"],
})
export class ShoppingCartComponent {
  constructor(private store: SharedStoreService, private mmPkgApi: MagicMirrorPackageAPI) {}

  @Input()
  public selectedPackages: Array<MagicMirrorPackage>;

  @Output()
  public selectedPackagesChange = new EventEmitter<Array<MagicMirrorPackage>>();

  @Input()
  public loading: boolean;

  @Output()
  public loadingChange = new EventEmitter<boolean>(false);

  async onCheckout() {
    if (this.selectedPackages === null) {
      return;
    }

    const remove = new Array<MagicMirrorPackage>();
    const install = new Array<MagicMirrorPackage>();

    for (const pkg of this.selectedPackages) {
      (pkg.is_installed ? remove : install).push(pkg);
    }

    this.selectedPackagesChange.emit([]);
    this.loadingChange.emit(true);

    if (remove) {
      const response = await this.mmPkgApi.postRemovePackages(remove);

      if (response.code === 200) {
        const installed = response.message as Array<MagicMirrorPackage>;
        console.log(`Removed ${installed.length} packages`);
      }
    }

    if (install) {
      const response = await this.mmPkgApi.postInstallPackages(install);

      if (response.code === 200) {
        const installed = response.message as Array<MagicMirrorPackage>;
        console.log(`Installed ${installed.length} packages`);
      }
    }

    this.store.getPackages();
  }
}
