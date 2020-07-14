import { Component, ViewChild, OnInit } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { SelectionModel } from "@angular/cdk/collections";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSort } from "@angular/material/sort";
import { MatPaginator, PageEvent } from "@angular/material/paginator";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { Subscription } from "rxjs";
import { TerminalStyledPopUpWindowComponent } from "src/app/components/terminal-styled-pop-up-window/terminal-styled-pop-up-window.component";
import { DataStoreService } from "src/app/services/data-store.service";
import { MagicMirrorTableUtility } from "src/app/utils/magic-mirror-table-utlity";
import { CustomSnackbarComponent } from "src/app/components/custom-snackbar/custom-snackbar.component";
import { MMPMUtility } from "src/app/utils/mmpm-utility";
import { ActiveProcessCountService } from "src/app/services/active-process-count.service";
import { ConfirmationDialogComponent } from "src/app/components/confirmation-dialog/confirmation-dialog.component";
import { URLS } from "src/app/utils/urls";

@Component({
  selector: "app-mmpm-local-packages",
  templateUrl: "./mmpm-local-packages.component.html",
  styleUrls: [
    "./mmpm-local-packages.component.scss",
    "../../shared-styles/shared-table-styles.scss"
  ],
})
export class MMPMLocalPackagesComponent implements OnInit {

  constructor(
    public dialog: MatDialog,
    private dataStore: DataStoreService,
    private api: RestApiService,
    private mSnackBar: MatSnackBar,
    private mmpmUtility: MMPMUtility,
    private activeProcessService: ActiveProcessCountService
  ) {}

  @ViewChild(MatPaginator, { static: true }) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;

  private snackbar: CustomSnackbarComponent = new CustomSnackbarComponent(this.mSnackBar);
  private installedPackagesSubscription: Subscription;
  private mmpmLocalPackagesPageSizeCookie: string = "MMPM-local-packages-page-size";

  public packages: MagicMirrorPackage[];
  public tableUtility: MagicMirrorTableUtility;
  public dataSource: MatTableDataSource<MagicMirrorPackage>;
  public selection = new SelectionModel<MagicMirrorPackage>(true, []);
  public snackbarSettings: object = { duration: 5000 };
  public isUpgradeable: Array<boolean>;
  public upgradeablePackages: Array<MagicMirrorPackage>;

  public ngOnInit(): void {
    this.setupTableData();

    if (!this.mmpmUtility.getCookie(this.mmpmLocalPackagesPageSizeCookie)) {
      this.mmpmUtility.setCookie(this.mmpmLocalPackagesPageSizeCookie, "10");
    }

    this.paginator.pageSize = Number(this.mmpmUtility.getCookie(this.mmpmLocalPackagesPageSizeCookie));
  }

  private setupTableData(): void {
    this.installedPackagesSubscription = this.dataStore.installedPackages.subscribe((pkgs) => {
      this.isUpgradeable = new Array<boolean>(pkgs.length);
      this.upgradeablePackages = new Array<MagicMirrorPackage>();
      this.isUpgradeable.fill(false);

      this.dataStore.upgradeablePackages.subscribe((upgradeable) => {
        this.upgradeablePackages = upgradeable;

        this.upgradeablePackages.forEach((upgradeablePackage: MagicMirrorPackage) => {
          pkgs.forEach((installedPkg: MagicMirrorPackage, index: number) => {
            if (this.mmpmUtility.isSamePackage(upgradeablePackage, installedPkg)) {
              this.isUpgradeable[index] = true;
            }
          });
        });
      });

      this.packages = pkgs;
      this.selection = new SelectionModel<MagicMirrorPackage>(true, []);
      this.dataSource = new MatTableDataSource<MagicMirrorPackage>(this.packages);
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;

      this.tableUtility = new MagicMirrorTableUtility(
        this.selection,
        this.dataSource,
        this.sort,
        this.dialog,
        this.activeProcessService
      );
    });
  }

  ngOnDestroy() {
    this.installedPackagesSubscription.unsubscribe();
  }

  public onUninstallPackages(): void {
    if (!this.selection?.selected?.length) return;

    const numPackages: number = this.selection.selected.length;

    const confirmationDialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        message: `${numPackages} ${numPackages === 1 ? "package" : "packages"} will be removed`
      },
      disableClose: true
    });

    confirmationDialogRef.afterClosed().subscribe((yes) => {
      if (!yes) return;
      let ids: Array<number> = this.tableUtility.saveProcessIds(this.selection.selected, "Removing");

      this.snackbar.notify("Executing ...");
      const selected = this.selection.selected;

      this.selection.clear();

      this.api.packagesRemove(selected).then((result: string) => {
        const failures: Array<object> = JSON.parse(result);

        if (failures.length) {
          const pkg = failures.length == 1 ? "package" : "packages";
          this.dialog.open(TerminalStyledPopUpWindowComponent, this.mmpmUtility.basicDialogSettings(failures));
          this.snackbar.error(`Failed to remove ${failures.length} ${pkg}`);

        } else {
          this.snackbar.success("Removed successfully!");
        }

        this.tableUtility.deleteProcessIds(ids);
        this.dataStore.loadData();

      }).catch((error) => console.log(error));
    });
  }

  public onUpgradeModules(): void {
    if (!this.selection?.selected?.length) return;

    const numPackages: number = this.selection.selected.length;

    const confirmationDialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        message: `${numPackages} ${numPackages === 1 ? "package" : "packages"} will be upgraded, if available`
      },
      disableClose: true
    });

    confirmationDialogRef.afterClosed().subscribe((yes) => {
      if (!yes) return;

      this.snackbar.notify("Executing ...");

      this.api.packagesUpgrade(this.selection.selected).then((fails) => {
        fails = JSON.parse(fails);

        if (fails.length) {
          const pkg = fails.length == 1 ? "package" : "packages";
          this.dialog.open(TerminalStyledPopUpWindowComponent, this.mmpmUtility.basicDialogSettings(fails));
          this.snackbar.error(`Failed to upgrade ${fails.length} ${pkg}`);
        } else {
          this.snackbar.success("Upgraded selected modules successfully!");
        }

      }).catch((error) => console.log(error));
    });
  }

  public setPaginationCookie(pageEvent?: PageEvent): void {
    this.mmpmUtility.setCookie(this.mmpmLocalPackagesPageSizeCookie, pageEvent.pageSize);
  }
}
