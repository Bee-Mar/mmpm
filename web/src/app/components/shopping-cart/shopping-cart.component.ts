import {MagicMirrorPackage} from "@/models/magicmirror-package";
import {MagicMirrorPackageAPI} from "@/services/api/magicmirror-package-api.service";
import {SharedStoreService} from "@/services/shared-store.service";
import {Component, Input, Output, EventEmitter} from "@angular/core";
import {ConfirmationService, MessageService} from "primeng/api";

@Component({
  selector: "app-shopping-cart",
  templateUrl: "./shopping-cart.component.html",
  styleUrls: ["./shopping-cart.component.scss"],
  providers: [MessageService, ConfirmationService],
})
export class ShoppingCartComponent {
  constructor(private store: SharedStoreService, private mmPkgApi: MagicMirrorPackageAPI, private msg: MessageService, private confirmation: ConfirmationService) {}

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
      message: 'Are you sure you want to install/remove the selected packages?',
      header: 'Confirmation',
      icon: 'pi pi-exclamation-triangle',
      accept: () => {
        this.checkout();
      },
      reject: () => {
        return;
      }
    });
  }

  async checkout() {
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
        this.msg.add({severity: "success", summary: "Remove Packages", detail: `Successfully removed ${removed.length}/${remove.length} selected packages`});
      } else {
        this.msg.add({severity: "error", summary: "Remove Packages", detail: response.message});
      }
    }

    if (install.length > 0) {
      const response = await this.mmPkgApi.postInstallPackages(install);

      if (response.code === 200) {
        const installed = response.message as Array<MagicMirrorPackage>;
        this.msg.add({severity: "success", summary: "Install Packages", detail: `Successfully installed ${installed.length}/${install.length} selected packages`});
      } else {
        this.msg.add({severity: "error", summary: "Install Packages", detail: response.message});
      }
    }

    this.store.load();
  }
}
