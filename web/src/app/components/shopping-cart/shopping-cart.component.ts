import { MagicMirrorPackage } from "@/models/magicmirror-package";
import { MagicMirrorPackageAPI } from "@/services/api/magicmirror-package-api.service";
import { SharedStoreService } from "@/services/shared-store.service";
import { Component, Input, Output, EventEmitter } from "@angular/core";
import { MessageService } from "primeng/api";

@Component({
  selector: "app-shopping-cart",
  templateUrl: "./shopping-cart.component.html",
  styleUrls: ["./shopping-cart.component.scss"],
  providers: [MessageService],
})
export class ShoppingCartComponent {
  constructor(private store: SharedStoreService, private mmPkgApi: MagicMirrorPackageAPI, private msg: MessageService) {}

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

    if (remove.length > 0) {
      const response = await this.mmPkgApi.postRemovePackages(remove);

      if (response.code === 200) {
        const removed = response.message as Array<MagicMirrorPackage>;
        this.msg.add({ severity: "success", summary: "Remove Packages", detail: `Successfully removed ${removed.length}/${remove.length} selected packages` });
      } else {
        this.msg.add({ severity: "error", summary: "Remove Packages", detail: response.message });
      }
    }

    if (install.length > 0) {
      const response = await this.mmPkgApi.postInstallPackages(install);

      if (response.code === 200) {
        const installed = response.message as Array<MagicMirrorPackage>;
        this.msg.add({ severity: "success", summary: "Remove Packages", detail: `Successfully removed ${installed.length}/${install.length} selected packages` });
      } else {
        this.msg.add({ severity: "error", summary: "Install Packages", detail: response.message });
      }
    }

    this.store.load();
  }
}
