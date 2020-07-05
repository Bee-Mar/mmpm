import { Component, ViewChild, ViewEncapsulation, OnInit } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { SelectionModel } from "@angular/cdk/collections";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSort } from "@angular/material/sort";
import { MatPaginator, PageEvent } from "@angular/material/paginator";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { TableUpdateNotifierService } from "src/app/services/table-update-notifier.service";
import { Subscription } from "rxjs";
import { TerminalStyledPopUpWindowComponent } from "src/app/components/terminal-styled-pop-up-window/terminal-styled-pop-up-window.component";
import { DataStoreService } from "src/app/services/data-store.service";
import { MagicMirrorTableUtility } from "src/app/utils/magic-mirror-table-utlity";
import { CustomSnackbarComponent } from "src/app/components/custom-snackbar/custom-snackbar.component";
import { MMPMUtility } from "src/app/utils/mmpm-utility";
import { ActiveProcessCountService } from "src/app/services/active-process-count.service";
import { InstallationConflict, MagicMirrorPackage } from "src/app/interfaces/interfaces";
import { ConfirmationDialogComponent } from "src/app/components/confirmation-dialog/confirmation-dialog.component";
import { InstallationConflictResolutionDialogComponent } from "src/app/components/installation-conflict-resolution-dialog/installation-conflict-resolution-dialog.component";

@Component({
  selector: "app-mmpm-marketplace",
  templateUrl: "./mmpm-marketplace.component.html",
  styleUrls: [
    "./mmpm-marketplace.component.scss",
    "../../shared-styles/shared-table-styles.scss"
  ],
  encapsulation: ViewEncapsulation.None
})
export class MMPMMarketplaceComponent implements OnInit {
  @ViewChild(MatPaginator, { static: true }) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;

  constructor(
    public dialog: MatDialog,
    private api: RestApiService,
    private dataStore: DataStoreService,
    private notifier: TableUpdateNotifierService,
    private mSnackBar: MatSnackBar,
    private mmpmUtility: MMPMUtility,
    private activeProcessService: ActiveProcessCountService
  ) {}

  public allPackages: MagicMirrorPackage[];
  public installedPackages: MagicMirrorPackage[];
  public tableUtility: MagicMirrorTableUtility;
  public dataSource: MatTableDataSource<MagicMirrorPackage>;
  public selection = new SelectionModel<MagicMirrorPackage>(true, []);

  private snackbar: CustomSnackbarComponent = new CustomSnackbarComponent(this.mSnackBar);
  private subscription: Subscription;
  private mmpmMarketplacePaginatorCookieSize: string = "MMPM-marketplace-packages-page-size";
  private magicmirrorRootDirectory: string;

  public ngOnInit(): void {
    this.setupTableData();

    this.subscription = this.notifier.getNotification().subscribe((_) => this.setupTableData(true));

    if (!this.mmpmUtility.getCookie(this.mmpmMarketplacePaginatorCookieSize)) {
      this.mmpmUtility.setCookie(this.mmpmMarketplacePaginatorCookieSize, 10);
    }

    this.paginator.pageSize = Number(this.mmpmUtility.getCookie(this.mmpmMarketplacePaginatorCookieSize));
  }

  private setupTableData(refresh: boolean = false): void {

    this.dataStore.getMagicMirrorRootDirectory(refresh).then((dir) => {
      this.magicmirrorRootDirectory = dir;
    }).catch((error) => console.log(error));

    this.dataStore.getAllAvailablePackages(refresh).then((allPackages: MagicMirrorPackage[]) => {
      this.dataStore.getAllInstalledPackages(refresh).then((installedPackages: MagicMirrorPackage[]) => {
        this.installedPackages = installedPackages;

        // removing all the packages that are currently installed from the list of available packages
        for (const installedPackage of installedPackages) {
          let index: number = allPackages.findIndex(
            (availablePackage: MagicMirrorPackage) =>
            availablePackage.repository === installedPackage.repository &&
            availablePackage.title === installedPackage.title &&
            availablePackage.author === installedPackage.author &&
            availablePackage.category === installedPackage.category
          );

          if (index > -1) allPackages.splice(index, 1);
        }

        this.allPackages = allPackages;
        this.selection = new SelectionModel<MagicMirrorPackage>(true, []);
        this.dataSource = new MatTableDataSource<MagicMirrorPackage>(this.allPackages);
        this.dataSource.paginator = this.paginator;
        this.dataSource.sort = this.sort;

        this.tableUtility = new MagicMirrorTableUtility(
          this.selection,
          this.dataSource,
          this.sort,
          this.dialog,
          this.activeProcessService
        );
      }).catch((error) => console.log(error));
    }).catch((error) => console.log(error));
  }

  private checkForInstallationConflicts(selectedPackages: MagicMirrorPackage[]): Promise<InstallationConflict> {
    let promise: Promise<InstallationConflict> = new Promise<InstallationConflict>((resolve, reject) => {

      let installationConflict: InstallationConflict = {
        matchesSelectedTitles: new Array<MagicMirrorPackage>(),
        matchesInstalledTitles: new Array<MagicMirrorPackage>()
      };

      this.dataStore.getAllInstalledPackages().then((installedPackages: MagicMirrorPackage[]) => {

        selectedPackages.forEach((selectedPackage: MagicMirrorPackage, index: number) => {
          const existing: MagicMirrorPackage = installedPackages.find((pkg: MagicMirrorPackage) => pkg.title === selectedPackage.title);

          if (existing) {
            installationConflict.matchesInstalledTitles.push(selectedPackage);
            selectedPackages.slice(index, 1);
          } else {

            let dups = selectedPackages.filter((pkg: MagicMirrorPackage) => pkg.title === selectedPackage.title);

            if (dups?.length > 1) {
              installationConflict.matchesSelectedTitles = installationConflict.matchesSelectedTitles.concat(dups);
              selectedPackages = selectedPackages.filter((pkg: MagicMirrorPackage) => pkg.title !== selectedPackage.title);
            }
          }
        });

        resolve(installationConflict);

      }).catch((error) => {
        console.log(error);
        reject(installationConflict);
      });
    });

    return promise;
  }

  private installPackages(selected: MagicMirrorPackage[]) {
    let ids: Array<number> = this.tableUtility.saveProcessIds(selected, "[ Installation ]");

    this.api.packagesInstall(selected).then((failures: string) => {
      failures = JSON.parse(failures);

      if (!failures.length) {
        this.snackbar.success("Installed successfully!");

      } else {
        const pkg = failures.length == 1 ? "package" : "packages";

        this.dialog.open(TerminalStyledPopUpWindowComponent, this.mmpmUtility.basicDialogSettings(failures));
        this.snackbar.error(`${failures.length} ${pkg} failed to install`);
      }

      this.tableUtility.deleteProcessIds(ids);
      this.notifier.triggerTableUpdate();

    }).catch((error) => console.log(error));
  }

  public onInstallPackages(): void {
    if (!this.selection?.selected?.length) return;

    const numPackages: number = this.selection.selected.length;

    const confirmationDialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        message: `${numPackages} ${numPackages === 1 ? "package" : "packages"} will be installed`
      },
      disableClose: true
    });

    confirmationDialogRef.afterClosed().subscribe((yes) => {
      if (!yes) return;

      const selected = this.selection.selected;
      this.selection.clear();

      this.checkForInstallationConflicts(selected).then((installationConflicts: InstallationConflict) => {

        if (!installationConflicts?.matchesSelectedTitles?.length && !installationConflicts?.matchesInstalledTitles?.length) {
          this.installPackages(selected);

        } else {
          let dialogRef = this.dialog.open(
            InstallationConflictResolutionDialogComponent,
            this.mmpmUtility.basicDialogSettings({
              matchesSelectedTitles: installationConflicts.matchesSelectedTitles,
              matchesInstalledTitles: installationConflicts.matchesInstalledTitles,
              magicmirrorRootDirectory: this.magicmirrorRootDirectory
            })
          );

          dialogRef.afterClosed().subscribe((updatedPackages: MagicMirrorPackage[]) => {
            if (!updatedPackages?.length) {
              return;
            }

            selected.forEach((selectedPackage: MagicMirrorPackage) => {
              updatedPackages.forEach((updatedPackage: MagicMirrorPackage) => {
                if (selectedPackage.title === updatedPackage.title && updatedPackage.directory.length) {
                  selectedPackage.directory = updatedPackage.directory;
                }
              });
            });

            this.installPackages(selected);
          });
        }
      }).catch((error) => console.log(error));
    });
  }

  public onRefreshPackages(): void {
    this.snackbar.notify("Executing ... ");
    this.setupTableData(true);
    this.snackbar.notify("Refresh complete!");
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  public setPaginationCookie(pageEvent?: PageEvent): void {
    this.mmpmUtility.setCookie(this.mmpmMarketplacePaginatorCookieSize, pageEvent.pageSize);
  }
}
