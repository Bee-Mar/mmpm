import { Component, OnInit, OnDestroy } from "@angular/core";
import { MagicMirrorPackage } from "@/magicmirror/models/magicmirror-package";
import { SharedStoreService } from "@/services/shared-store.service";
import { MagicMirrorPackageAPI } from "@/services/api/magicmirror-package-api.service";
import { APIResponse, BaseAPI } from "@/services/api/base-api";
import { Subscription } from "rxjs";

interface Icon {
  logo: string;
  color: string;
}

@Component({
  selector: "app-mmpm-marketplace",
  templateUrl: "./mmpm-marketplace.component.html",
  styleUrls: ["./mmpm-marketplace.component.scss"],
})
export class MmpmMarketPlaceComponent implements OnInit, OnDestroy {
  constructor(private store: SharedStoreService, private mm_pkg_api: MagicMirrorPackageAPI, private base_api: BaseAPI) {}

  private subscription: Subscription = new Subscription();
  public packages: Array<MagicMirrorPackage> = new Array<MagicMirrorPackage>();
  public selected_packages: Array<MagicMirrorPackage> = new Array<MagicMirrorPackage>();
  public loading = true;
  public total_records = 0;

  public icons: { [key: string]: Icon } = {
    Finance: {
      logo: "fa-solid fa-sack-dollar",
      color: "#ffff4d",
    },
    Sports: {
      logo: "fa-solid fa-baseball-bat-ball",
      color: "#ffff99",
    },
    "Entertainment / Misc": {
      logo: "fa-solid fa-shuffle",
      color: "teal",
    },
    Education: {
      logo: "fa-solid fa-graduation-cap",
      color: "gray",
    },
    "Utility / IoT / 3rd Party / Integration": {
      logo: "fa-solid fa-wrench",
      color: "gray",
    },
    "Voice Control": {
      logo: "fa-solid fa-microphone",
      color: "#ccff99",
    },
    Weather: {
      logo: "fa-solid fa-cloud",
      color: "white",
    },
    "News / Information": {
      logo: "fa-solid fa-envelope-open-text",
      color: "#0099ff",
    },
    Religion: {
      logo: "fa-solid fa-cross",
      color: "#996633",
    },
    Health: {
      logo: "fa-solid fa-heart",
      color: "red",
    },
    "Transport / Travel": {
      logo: "fa-solid fa-plane",
      color: "#999966",
    },
    "Outdated modules": {
      logo: "fa-solid fa-clock",
      color: "",
    },
    "Development / Core MagicMirror²": {
      logo: "fa-solid fa-desktop",
      color: "#00cc99",
    },
  };

  ngOnInit(): void {
    this.subscription = this.store.packages.subscribe((packages: Array<MagicMirrorPackage>) => {
      this.packages = packages;
      this.loading = false;
      this.total_records = this.packages.length;
    });
  }

  ngOnDestroy(): void {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  // Angular doesn't let you cast the Event directly in templates {-_-}
  public get_input_value(event: Event) {
    return (event.target as HTMLInputElement).value;
  }

  public install(pkgs: MagicMirrorPackage[]): void {
    this.mm_pkg_api
      .post_install_packages(pkgs)
      .then((_) => {
        this.store.get_packages();
      })
      .catch((error) => console.log(error));
  }

  public remove(pkgs: MagicMirrorPackage[]): void {
    this.mm_pkg_api
      .post_remove_packages(pkgs)
      .then((_) => {
        this.store.get_packages();
      })
      .catch((error) => console.log(error));
  }

  public upgrade(pkgs: MagicMirrorPackage[]): void {
    this.mm_pkg_api
      .post_upgrade_packages(pkgs)
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
