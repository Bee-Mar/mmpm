import {Component, OnInit, OnDestroy} from "@angular/core";
import {MagicMirrorPackage} from "@/magicmirror/models/magicmirror-package";
import {SharedStoreService} from "@/services/shared-store.service";
import {MagicMirrorPackageAPI} from "@/services/api/magicmirror-package-api.service";
import {APIResponse, BaseAPI} from "@/services/api/base-api";
import {Subscription} from "rxjs";
import {MarketPlaceIcons, DefaultMarketPlaceIcon} from './marketplace-icons.model';

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
  public total_records = 0;

  ngOnInit(): void {
    this.subscription = this.store.packages.subscribe((packages: Array<MagicMirrorPackage>) => {
      this.packages = packages;
      this.loading = false;
      this.total_records = this.packages.length;

      this.categories = this.packages
        .map(pkg => pkg.category)
        .filter((category, index, self) => self.indexOf(category) === index);

      // add a default icon for any category that isn't recognized above
      this.packages.forEach(pkg => {
        if (pkg.category && !this.icons[pkg.category]) {
          this.icons[pkg.category] = {...this.default_icon};
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
    console.log(this.selected_packages);
    return (event.target as HTMLInputElement).value;
  }

  public install(): void {
    this.mm_pkg_api
      .post_install_packages(this.selected_packages)
      .then((_) => {
        this.store.get_packages();
      })
      .catch((error) => console.log(error));
  }

  public remove(): void {
    this.mm_pkg_api
      .post_remove_packages(this.selected_packages)
      .then((_) => {
        this.store.get_packages();
      })
      .catch((error) => console.log(error));
  }

  public upgrade(): void {
    this.mm_pkg_api
      .post_upgrade_packages(this.selected_packages)
      .then((_) => {
        this.store.get_packages();
      })
      .catch((error) => console.log(error));
  }

  public add_mm_pkg(pkg: MagicMirrorPackage): void {
    this.mm_pkg_api
      .post_add_mm_pkg(pkg)
      .then((_) => {
        this.store.get_packages();
      })
      .catch((error) => console.log(error));
  }

  public remove_mm_pkg(pkg: MagicMirrorPackage): void {
    this.mm_pkg_api
      .post_add_mm_pkg(pkg)
      .then((_) => {
        this.store.get_packages();
      })
      .catch((error) => console.log(error));
  }

  public refresh_db(): void {
    this.base_api.get_("db/refresh").then((response: APIResponse) => {
      if (response.message === true) {
        this.store.get_packages();
      } else {
        console.log("Failed to update database");
      }
    });
  }
}

