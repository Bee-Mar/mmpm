import { Component, OnInit, OnDestroy } from "@angular/core";
import { MagicMirrorPackage, RemotePackageDetails } from "@/models/magicmirror-package";
import { SharedStoreService } from "@/services/shared-store.service";
import { MagicMirrorPackageAPI } from "@/services/api/magicmirror-package-api.service";
import { Subscription } from "rxjs";
import { MarketPlaceIcons, DefaultMarketPlaceIcon } from "./marketplace-icons.model";
import { MessageService } from "primeng/api";

@Component({
  selector: "app-mmpm-marketplace",
  templateUrl: "./mmpm-marketplace.component.html",
  styleUrls: ["./mmpm-marketplace.component.scss"],
  providers: [MessageService],
})
export class MmpmMarketPlaceComponent implements OnInit, OnDestroy {
  constructor(private store: SharedStoreService, private mmPkgApi: MagicMirrorPackageAPI) {}

  private packagesSubscription: Subscription = new Subscription();
  private defaultIcon = DefaultMarketPlaceIcon;

  public icons = MarketPlaceIcons;
  public packages = new Array<MagicMirrorPackage>();
  public categories = new Array<string>();
  public selectedPackages = new Array<MagicMirrorPackage>();
  public loading = true;
  public readonly installedOptions = [true, false];
  public selectedInstalled: boolean | null = null;
  public selectedPackage: MagicMirrorPackage | null = null;
  public displayDetailsDialog = false;
  public selectedCategories = new Array<string>();

  public ngOnInit(): void {
    this.packagesSubscription = this.store.packages.subscribe((packages: Array<MagicMirrorPackage>) => {
      this.packages = packages;

      this.categories = this.packages.map((pkg) => pkg.category).filter((category, index, self) => self.indexOf(category) === index);

      // add a default icon for any category that isn't recognized above
      this.packages.forEach((pkg: MagicMirrorPackage) => {
        if (pkg.category && !this.icons[pkg.category]) {
          this.icons[pkg.category] = { ...this.defaultIcon };
        }

        this.loading = false;
      });
    });
  }

  public ngOnDestroy(): void {
    this.packagesSubscription.unsubscribe();
  }

  async onCheckout() {
    const remove = new Array<MagicMirrorPackage>();
    const install = new Array<MagicMirrorPackage>();

    for (const pkg of this.selectedPackages) {
      (pkg.is_installed ? remove : install).push(pkg);
    }

    this.selectedPackages = [];
    this.loading = true;

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
