import { Component, Input, OnDestroy, OnInit, Output, EventEmitter } from "@angular/core";
import { DatabaseInfo } from "@/magicmirror/models/database-details";
import { Subscription } from "rxjs";
import { APIResponse, BaseAPI } from "@/services/api/base-api";
import { SharedStoreService } from "@/services/shared-store.service";
import { MagicMirrorPackage } from "@/magicmirror/models/magicmirror-package";

@Component({
  selector: "app-database-info",
  templateUrl: "./database-info.component.html",
  styleUrls: ["./database-info.component.scss"],
})
export class DatabaseInfoComponent implements OnInit, OnDestroy {
  constructor(private baseApi: BaseAPI, private store: SharedStoreService) {}

  private dbInfoSubscription: Subscription = new Subscription();

  @Input()
  public loading: boolean;

  @Output()
  public loadingChange = new EventEmitter<boolean>(false);

  public dbInfo: DatabaseInfo;
  public displayDbInfoDialog = false;
  public displayDbUpgradeDialog = false;
  public selectedPackages = new Array<MagicMirrorPackage>();
  public version = "";

  public database_options = [
    {
      label: "Update",
      icon: "fa-solid fa-arrows-rotate",
      command: () => {
        this.update_db();
      },
    },
    {
      label: "Upgrade",
      icon: "fa-solid fa-arrow-up-from-bracket",
      command: () => {
        console.log("Upgrade");
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
  }

  public ngOnDestroy(): void {
    this.dbInfoSubscription.unsubscribe();
  }

  private update_db(): void {
    this.loading = true;
    this.loadingChange.emit(this.loading);

    // TODO: this isn't correct now. It needs to be a POST and also make a call
    // to the endpoint that checks if magicmirror is upgradable
    this.baseApi.get_("db/update").then((response: APIResponse) => {
      if (response.code === 200 && response.message === true) {
        this.store.getPackages();
      } else {
        console.log("Failed to update database");
      }
    });
  }

  /*
  private upgrade_db(): void {
    this.loading = true;

    this.mmPkgApi
      .post_upgrade_packages(this.selected)
      .then((response: APIResponse) => {
        if (response.code === 200) {
          this.store.getPackages();
        }
      })
      .catch((error) => console.log(error));
  }
  */
}
