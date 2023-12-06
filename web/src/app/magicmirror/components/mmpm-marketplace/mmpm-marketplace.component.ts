import { Component, OnInit, OnDestroy } from "@angular/core";
import { MagicMirrorPackage, RemotePackageDetails } from "@/magicmirror/models/magicmirror-package";
import { SharedStoreService } from "@/services/shared-store.service";
import { MagicMirrorPackageAPI } from "@/services/api/magicmirror-package-api.service";
import { APIResponse, BaseAPI } from "@/services/api/base-api";
import { Subscription } from "rxjs";
import { MarketPlaceIcons, DefaultMarketPlaceIcon } from "./marketplace-icons.model";

@Component({
  selector: "app-mmpm-marketplace",
  templateUrl: "./mmpm-marketplace.component.html",
  styleUrls: ["./mmpm-marketplace.component.scss"],
})
export class MmpmMarketPlaceComponent implements OnInit, OnDestroy {
  constructor(private store: SharedStoreService, private mm_pkg_api: MagicMirrorPackageAPI, private base_api: BaseAPI) {}

  private subscription: Subscription = new Subscription();
  private default_icon = DefaultMarketPlaceIcon;

  public icons = MarketPlaceIcons;
  public packages: Array<MagicMirrorPackage> = new Array<MagicMirrorPackage>();
  public categories: Array<string> = new Array<string>();
  public selected_packages: Array<MagicMirrorPackage> = new Array<MagicMirrorPackage>();
  public loading = true;
  public readonly installed_options = [true, false];
  public selected_installed: boolean | null = null;
  public selected_package: MagicMirrorPackage | null = null;
  public display_details_dialog = false;
  public display_custom_pkg_add_dialog = false;
  public display_custom_pkg_remove_dialog = false;
  public loading_package_data = false;
  public custom_packages = new Array<MagicMirrorPackage>();
  public selected_custom_packages = new Array<MagicMirrorPackage>();
  public custom_package: MagicMirrorPackage = this.clear_custom_package();

  public custom_package_options = [
    {
      label: "Add",
      icon: "fa-solid fa-plus",
      command: () => {
        this.custom_package = this.clear_custom_package();

        if (this.display_custom_pkg_remove_dialog) {
          this.display_custom_pkg_remove_dialog = false;
        }

        this.display_custom_pkg_add_dialog = true;
      },
    },
    {
      label: "Remove",
      icon: "fa-solid fa-eraser",
      command: () => {
        if (this.display_custom_pkg_add_dialog) {
          this.display_custom_pkg_add_dialog = false;
        }

        this.display_custom_pkg_remove_dialog = true;
      },
    },
  ];

  ngOnInit(): void {
    this.subscription = this.store.packages.subscribe((packages: Array<MagicMirrorPackage>) => {
      this.packages = packages;
      this.loading = false;
      this.custom_packages = [];

      this.categories = this.packages.map((pkg) => pkg.category).filter((category, index, self) => self.indexOf(category) === index);

      // add a default icon for any category that isn't recognized above
      this.packages.forEach((pkg) => {
        if (pkg.category === "External Packages") {
          this.custom_packages.push(pkg);
        }

        if (pkg.category && !this.icons[pkg.category]) {
          this.icons[pkg.category] = { ...this.default_icon };
        }
      });
    });
  }

  ngOnDestroy(): void {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  // Angular doesn't let you cast the Event directly in templates {-_-}
  public get_input_value(event: Event): string {
    return (event.target as HTMLInputElement).value;
  }

  async on_confirm_shopping_cart() {
    const packages_to_remove = new Array<MagicMirrorPackage>();
    const packages_to_install = new Array<MagicMirrorPackage>();

    for (const pkg of this.selected_packages) {
      (pkg.is_installed ? packages_to_remove : packages_to_install).push(pkg);
    }

    this.selected_packages = [];
    this.loading = true;

    if (packages_to_remove) {
      const response = await this.mm_pkg_api.post_remove_packages(packages_to_remove);

      if (response.code === 200) {
        const installed = response.message as Array<MagicMirrorPackage>;
        console.log(`Removed ${installed.length} packages`);
      }
    }

    if (packages_to_install) {
      const response = await this.mm_pkg_api.post_install_packages(packages_to_install);

      if (response.code === 200) {
        const installed = response.message as Array<MagicMirrorPackage>;
        console.log(`Installed ${installed.length} packages`);
      }
    }

    this.store.get_packages();
  }

  public on_upgrade(): void {
    this.loading = true;

    this.mm_pkg_api
      .post_upgrade_packages(this.selected_packages)
      .then((response: APIResponse) => {
        if (response.code === 200) {
          this.store.get_packages();
        }
      })
      .catch((error) => console.log(error));
  }

  public on_add_mm_pkg(): void {
    this.loading = true;

    this.mm_pkg_api
      .post_add_mm_pkg(this.custom_package)
      .then((response: APIResponse) => {
        if (response.code === 200) {
          this.store.get_packages();
          console.log(response);
          this.custom_package = this.clear_custom_package();
        }
      })
      .catch((error) => console.log(error));
  }

  public on_remove_mm_pkg(): void {
    this.mm_pkg_api
      .post_remove_mm_pkgs(this.selected_custom_packages)
      .then((response: APIResponse) => {
        if (response.code === 200) {
          this.store.get_packages();
        }
      })
      .catch((error) => console.log(error));
  }

  public on_refresh_db(): void {
    this.loading = true;

    this.base_api.get_("db/refresh").then((response: APIResponse) => {
      if (response.code === 200 && response.message === true) {
        this.store.get_packages();
      } else {
        console.log("Failed to update database");
      }
    });
  }

  public on_package_details(pkg: MagicMirrorPackage): void {
    this.selected_package = pkg;
    this.display_details_dialog = true;

    if (typeof pkg?.remote_details != "undefined") {
      console.log(`${pkg.title} already has remote_details stored`);
      this.loading_package_data = false;
      return;
    }

    this.loading_package_data = true;
    console.log(`${pkg.title} does not have remote_details stored. Collecting...`);

    this.mm_pkg_api
      .post_details(pkg)
      .then((response: APIResponse) => {
        if (response.code === 200) {
          pkg.remote_details = response.message as RemotePackageDetails;
          console.log(`Retrieved remote details for ${pkg.title}`);
          this.loading_package_data = false;
        }
      })
      .catch((error) => {
        console.log(error);
        // failed getting remote details (probably because we exceeded the request count)
        // so we need to still display the content
        this.loading_package_data = false;
      });
  }

  private clear_custom_package(): MagicMirrorPackage {
    return {
      title: "",
      repository: "",
      author: "",
      description: "",
      directory: "",
      is_installed: false,
      is_upgradable: false,
      category: "External Packages",
      remote_details: {
        stars: 0,
        forks: 0,
        issues: 0,
        created: "",
        last_updated: "",
      },
    };
  }
}
