import { Component, OnInit, OnDestroy } from "@angular/core";
import { MagicMirrorPackage, RemotePackageDetails } from "@/models/magicmirror-package";
import { SharedStoreService } from "@/services/shared-store.service";
import { MagicMirrorPackageAPI } from "@/services/api/magicmirror-package-api.service";
import { APIResponse } from "@/services/api/base-api";
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
  public loadingPackageDetails = false;
  public selectedCategories = new Array<string>();

  public ngOnInit(): void {
    this.packagesSubscription = this.store.packages.subscribe((packages: Array<MagicMirrorPackage>) => {
      this.packages = packages;

      this.categories = this.packages.map((pkg) => pkg.category).filter((category, index, self) => self.indexOf(category) === index);

      // add a default icon for any category that isn't recognized above
      this.packages.forEach((pkg) => {
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

  public on_package_details(pkg: MagicMirrorPackage): void {
    this.selectedPackage = pkg;
    this.displayDetailsDialog = true;

    if (typeof pkg?.remote_details != "undefined") {
      console.log(`${pkg.title} already has remote_details stored`);
      this.loadingPackageDetails = false;
      return;
    }

    this.loadingPackageDetails = true;
    console.log(`${pkg.title} does not have remote_details stored. Collecting...`);

    this.mmPkgApi
      .postDetails(pkg)
      .then((response: APIResponse) => {
        if (response.code === 200) {
          pkg.remote_details = response.message as RemotePackageDetails;
          console.log(`Retrieved remote details for ${pkg.title}`);
          this.loadingPackageDetails = false;
        }
      })
      .catch((error) => {
        console.log(error);
        // failed getting remote details (probably because we exceeded the request count)
        // so we need to still display the content
        this.loadingPackageDetails = false;
      });
  }
}
