import { MagicMirrorPackage } from "@/models/magicmirror-package";
import { MagicMirrorPackageAPI } from "@/services/api/magicmirror-package-api.service";
import { SharedStoreService } from "@/services/shared-store.service";
import { Component, Input, Output, EventEmitter } from "@angular/core";
import { ConfirmationService, MessageService } from "primeng/api";

@Component({
  selector: "app-shopping-cart",
  templateUrl: "./shopping-cart.component.html",
  styleUrls: ["./shopping-cart.component.scss"],
  providers: [MessageService, ConfirmationService],
})
export class ShoppingCartComponent {
  constructor(
    private store: SharedStoreService,
    private mmPkgApi: MagicMirrorPackageAPI,
    private msg: MessageService,
    private confirmation: ConfirmationService,
  ) {}

  @Input()
  public selectedPackages: Array<MagicMirrorPackage>;

  @Output()
  public selectedPackagesChange = new EventEmitter<Array<MagicMirrorPackage>>();

  @Input()
  public loading: boolean;

  @Output()
  public loadingChange = new EventEmitter<boolean>(false);

  public onCheckout(): void {
    this.confirmation.confirm({
      message: "Are you sure you want to install/remove the selected packages?",
      header: "Confirmation",
      icon: "pi pi-exclamation-triangle",
      accept: () => {
        this.checkout();
      },
      reject: () => {
        return;
      },
    });
  }

  async checkout() {
    if (this.selectedPackages === null) {
      return;
    }

    const toRemove = new Array<MagicMirrorPackage>();
    const toInstall = new Array<MagicMirrorPackage>();

    for (const pkg of this.selectedPackages) {
      (pkg.is_installed ? toRemove : toInstall).push(pkg);
    }

    this.selectedPackagesChange.emit([]);
    this.loadingChange.emit(true);

    if (toRemove.length > 0) {
      const response = await this.mmPkgApi.postRemovePackages(toRemove);
      const success = response.message.success as Array<MagicMirrorPackage>;
      const failure = response.message.failure as Array<MagicMirrorPackage>;

      this.store.load();

      if (success.length) {
        this.msg.add({ severity: "success", summary: "Remove Packages", detail: `Successfully removed: ${success.map((pkg) => pkg.title).join(", ")}` });
      }

      if (failure.length) {
        this.msg.add({ severity: "error", summary: "Remove Packages", detail: `Failed to remove: ${failure.map((pkg) => pkg.title).join(", ")}` });
      }
    }

    if (toInstall.length > 0) {
      const response = await this.mmPkgApi.postInstallPackages(toInstall);
      const success = response.message.success as Array<MagicMirrorPackage>;
      const failure = response.message.failure as Array<MagicMirrorPackage>;

      this.store.load();

      if (success.length) {
        this.msg.add({ severity: "success", summary: "Install Packages", detail: `Successfully installed: ${success.map((pkg) => pkg.title).join(", ")}` });
      }

      if (failure.length) {
        this.msg.add({
          severity: "error",
          summary: "Install Packages",
          detail: `Failed to install: ${failure.map((pkg) => pkg.title).join(", ")}. See logs for details, and try reinstalling manually.`,
        });
      }
    }
  }
}
