import {Component, OnInit, OnDestroy} from "@angular/core";
import {MagicMirrorPackage} from "@/models/magicmirror-package";
import {SharedStoreService} from "@/services/shared-store.service";
import {Subscription} from "rxjs";
import {MarketPlaceIcons, DefaultMarketPlaceIcon} from "./marketplace-icons.model";

@Component({
  selector: "app-marketplace",
  templateUrl: "./marketplace.component.html",
  styleUrls: ["./marketplace.component.scss"],
})
export class MarketPlaceComponent implements OnInit, OnDestroy {
  constructor(private store: SharedStoreService) {}

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
          this.icons[pkg.category] = {...this.defaultIcon};
        }
      });

      this.loading = false;
    });
  }

  public ngOnDestroy(): void {
    this.packagesSubscription.unsubscribe();
  }
}
