import { MagicMirrorPackage } from "@/models/magicmirror-package";
import { APIResponse } from "@/services/api/base-api";
import { MagicMirrorPackageAPI } from "@/services/api/magicmirror-package-api.service";
import { SharedStoreService } from "@/services/shared-store.service";
import { Component, OnInit, ViewChild, Input, Output, EventEmitter, OnDestroy } from "@angular/core";
import { NgForm } from "@angular/forms";
import { MessageService } from "primeng/api";
import { Subscription } from "rxjs";

@Component({
  selector: "app-custom-package-manager",
  templateUrl: "./custom-package-manager.component.html",
  styleUrls: ["./custom-package-manager.component.scss"],
  providers: [MessageService],
})
export class CustomPackageManagerComponent implements OnInit, OnDestroy {
  constructor(
    private store: SharedStoreService,
    private mmPkgApi: MagicMirrorPackageAPI,
    private msg: MessageService,
  ) {}

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
      this.customPackages = packages.filter((pkg: MagicMirrorPackage) => pkg.category === "Custom Packages");
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
      category: "Custom Packages",
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
    this.loadingChange.emit(true);

    this.mmPkgApi
      .postAddMmPkg(this.customPackage)
      .then((response: APIResponse) => {
        this.reset();
        this.store.load();

        if (response.code === 200) {
          this.msg.add({ severity: "success", summary: "Add Custom Package", detail: `Successfully added ${this.customPackage.title} to database` });
        } else {
          this.msg.add({ severity: "error", summary: "Add Custom Package", detail: response.message });
        }
      })
      .catch((error) => {
        this.reset();
        this.store.load();
        console.log(error);
      });
  }

  public onRemoveMmPkg(): void {
    this.loadingChange.emit(true);

    this.mmPkgApi
      .postRemoveMmPkgs(this.selectedCustomPackages)
      .then((response: APIResponse) => {
        this.reset();
        this.store.load();

        const success = response.message.success as Array<MagicMirrorPackage>;
        const failure = response.message.failure as Array<MagicMirrorPackage>;

        if (success.length) {
          this.msg.add({ severity: "success", summary: "Remove Custom Packages", detail: `Successfully removed custom packages: ${success.map((pkg) => pkg.title).join(", ")}` });
        }

        if (failure.length) {
          this.msg.add({
            severity: "error",
            summary: "Remove Custom Packages",
            detail: `Failed to remove custom packages: ${failure.map((pkg) => pkg.title).join(", ")}. See logs for details.`,
          });
        }
      })
      .catch((error) => {
        this.reset();
        this.store.load();
        console.log(error);
      });
  }

  public reset(): void {
    this.customPackage = this.clearCustomPackage();
    this.customPackageForm.reset();
  }
}
