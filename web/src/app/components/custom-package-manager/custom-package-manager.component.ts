import { MagicMirrorPackage } from "@/models/magicmirror-package";
import { APIResponse } from "@/services/api/base-api";
import { MagicMirrorPackageAPI } from "@/services/api/magicmirror-package-api.service";
import { SharedStoreService } from "@/services/shared-store.service";
import { Component, OnInit, ViewChild, Input, Output, EventEmitter, OnDestroy } from "@angular/core";
import { NgForm } from "@angular/forms";
import { Subscription } from "rxjs";

@Component({
  selector: "app-custom-package-manager",
  templateUrl: "./custom-package-manager.component.html",
  styleUrls: ["./custom-package-manager.component.scss"],
})
export class CustomPackageManagerComponent implements OnInit, OnDestroy {
  constructor(private store: SharedStoreService, private mmPkgApi: MagicMirrorPackageAPI) {}

  private packagesSubscription: Subscription = new Subscription();

  @ViewChild("customPackageForm")
  public customPackageForm: NgForm;

  @Input()
  public loading: boolean;

  @Output()
  public loadingChange = new EventEmitter<boolean>(false);

  public displayCustomPkgAddDialog = false;
  public displayCustomPkgRemoveDialog = false;
  public selectedCustomPackages = new Array<MagicMirrorPackage>();
  public customPackages = new Array<MagicMirrorPackage>();
  public customPackage: MagicMirrorPackage = this.clearCustomPackage();

  public customPackageOptions = [
    {
      label: "Add",
      icon: "fa-solid fa-plus",
      command: () => {
        this.customPackage = this.clearCustomPackage();

        if (this.displayCustomPkgRemoveDialog) {
          this.displayCustomPkgRemoveDialog = false;
        }

        this.displayCustomPkgAddDialog = true;
      },
    },
    {
      label: "Remove",
      icon: "fa-solid fa-eraser",
      command: () => {
        if (this.displayCustomPkgAddDialog) {
          this.displayCustomPkgAddDialog = false;
        }

        this.displayCustomPkgRemoveDialog = true;
      },
    },
  ];

  public ngOnInit(): void {
    this.packagesSubscription = this.store.packages.subscribe((packages: Array<MagicMirrorPackage>) => {
      this.customPackages = packages.filter((pkg: MagicMirrorPackage) => pkg.category === "External Packages");
    });
  }

  public ngOnDestroy(): void {
    this.packagesSubscription.unsubscribe();
  }

  private clearCustomPackage(): MagicMirrorPackage {
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

  public onAddMmPkg(): void {
    this.loading = true;
    this.loadingChange.emit(this.loading);

    this.mmPkgApi
      .postAddMmPkg(this.customPackage)
      .then((response: APIResponse) => {
        if (response.code === 200) {
          this.store.load();
          console.log(response);
          this.customPackage = this.clearCustomPackage();
          this.customPackageForm.reset();
        }

        this.loading = false;
        this.loadingChange.emit(this.loading);
      })
      .catch((error) => console.log(error));
  }

  public onRemoveMmPkg(): void {
    this.loading = true;
    this.loadingChange.emit(this.loading);

    this.mmPkgApi
      .postRemoveMmPkgs(this.selectedCustomPackages)
      .then((response: APIResponse) => {
        if (response.code === 200) {
          this.store.load();
        }

        this.loading = false;
        this.loadingChange.emit(this.loading);
      })
      .catch((error) => console.log(error));
  }
}
