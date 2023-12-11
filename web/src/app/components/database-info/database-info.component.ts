import {Component, Input, OnDestroy, OnInit, Output, EventEmitter} from "@angular/core";
import {DatabaseInfo} from "@/models/database-details";
import {Subscription} from "rxjs";
import {APIResponse, BaseAPI} from "@/services/api/base-api";
import {SharedStoreService} from "@/services/shared-store.service";
import {MagicMirrorPackage} from "@/models/magicmirror-package";
import {UpgradableDetails} from "@/models/upgradable-details";
import {MagicMirrorPackageAPI} from "@/services/api/magicmirror-package-api.service";
import {MagicMirrorAPI} from "@/services/api/magicmirror-api.service";

@Component({
  selector: "app-database-info",
  templateUrl: "./database-info.component.html",
  styleUrls: ["./database-info.component.scss"],
})
export class DatabaseInfoComponent implements OnInit, OnDestroy {
  constructor(private baseApi: BaseAPI, private mmPkgApi: MagicMirrorPackageAPI, private store: SharedStoreService, private mmApi: MagicMirrorAPI) {}

  private dbInfoSubscription: Subscription = new Subscription();
  private upgradableSubscription: Subscription = new Subscription();

  @Input()
  public loading: boolean;

  @Output()
  public loadingChange = new EventEmitter<boolean>(false);

  public version = "";
  public dbInfo: DatabaseInfo;
  public upgradesAvailable = false;
  public displayDbInfoDialog = false;
  public displayDbUpgradeDialog = false;
  public upgradableItems = new Array<MagicMirrorPackage>();
  public selectedPackages = new Array<MagicMirrorPackage>();
  public selectedUpgrades = new Array<MagicMirrorPackage>();

  public databaseOptions = [
    {
      label: "Update",
      icon: "fa-solid fa-arrows-rotate",
      command: () => {
        this.onUpdate();
      },
    },
    {
      label: "Upgrades",
      icon: "fa-solid fa-arrow-up-from-bracket",
      command: () => {
        this.displayDbUpgradeDialog = true;
      },
    },
    {
      label: "Info",
      icon: "fa-solid fa-circle-info",
      command: () => {
        this.displayDbInfoDialog = true;
      },
    },
  ];

  public ngOnInit(): void {
    this.baseApi.get_("mmpm/version").then((response: APIResponse) => {
      this.version = response.message;
    });

    this.dbInfoSubscription = this.store.dbInfo.subscribe((info: DatabaseInfo) => {
      this.dbInfo = info;
    });

    this.upgradableSubscription = this.store.upgradable.subscribe((upgradable: UpgradableDetails) => {
      this.upgradableItems = [];
      this.upgradesAvailable = Boolean(upgradable && (upgradable.mmpm || upgradable.MagicMirror || upgradable.packages.length));

      this.upgradableItems.push(...upgradable.packages);

      if (upgradable.mmpm) {
        this.upgradableItems.push(this.dummyPackage("MMPM"));
      }

      if (upgradable.MagicMirror) {
        this.upgradableItems.push(this.dummyPackage("MagicMirror"));
      }

      if (this.upgradableItems.length) {
        this.databaseOptions[1].label = `Upgrades (${this.upgradableItems.length})`;
      }
    });
  }

  public ngOnDestroy(): void {
    this.dbInfoSubscription.unsubscribe();
    this.upgradableSubscription.unsubscribe();
  }

  private onUpdate(): void {
    this.loadingChange.emit(true);

    this.baseApi.get_("db/update").then((response: APIResponse) => {
      if (response.code === 200) {
        this.store.load();
        this.loadingChange.emit(false);
      } else {
        console.log("Failed to update database");
      }
    });
  }

  async onUpgrade() {
    const packages = this.selectedUpgrades.filter((pkg: MagicMirrorPackage) => pkg.title !== "MMPM" && pkg.title !== "MagicMirror");

    this.selectedUpgrades = [];
    this.loadingChange.emit(true);

    if (this.selectedUpgrades.findIndex((pkg: MagicMirrorPackage) => pkg.title === "MMPM") !== -1) {
      console.log("mmpm");
      // TODO: make this a toast pop up with a message or something else to let the user know
    }

    if (this.selectedUpgrades.findIndex((pkg: MagicMirrorPackage) => pkg.title === "MagicMirror") !== -1) {
      const response = await this.mmApi.getUpgrade();

      if (response.code !== 200) {
        console.log(response.message);
      }
    }

    if (packages.length) {
      const response = await this.mmPkgApi.postUpgradePackages(packages);

      if (response.code !== 200) {
        console.log(response.message);
      }
    }

    // the update endpoint will write out which packages have updates, and this needs
    // to get updated again following the actual upgrades
    const response = await this.baseApi.get_("db/update");

    if (response.code !== 200) {
      console.log(response.message);
    }

    this.store.load();
    this.loadingChange.emit(false);
  }

  private dummyPackage(title: string): MagicMirrorPackage {
    return {
      title: title,
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
