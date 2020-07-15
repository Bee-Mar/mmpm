import { Component, ViewChild, ViewEncapsulation, OnInit } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { SelectionModel } from "@angular/cdk/collections";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSort } from "@angular/material/sort";
import { MatPaginator, PageEvent } from "@angular/material/paginator";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
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
  encapsulation: ViewEncapsulation.None,
})
export class MMPMMarketplaceComponent implements OnInit {
  @ViewChild(MatPaginator, { static: true }) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;

  constructor(
    public dialog: MatDialog,
    private dataStore: DataStoreService,
    private api: RestApiService,
    private mSnackBar: MatSnackBar,
    private mmpmUtility: MMPMUtility,
    private activeProcessService: ActiveProcessCountService
  ) {}

  public allPackages: MagicMirrorPackage[];
  public installedPackages: MagicMirrorPackage[];
  public externalPackages: MagicMirrorPackage[];  public tableUtility: MagicMirrorTableUtility;
  public dataSource: MatTableDataSource<MagicMirrorPackage>;
  public selection = new SelectionModel<MagicMirrorPackage>(true, []);

  private snackbar: CustomSnackbarComponent = new CustomSnackbarComponent(this.mSnackBar);
  private subscription: Subscription;
  private mmpmMarketplacePaginatorCookieSize: string = "MMPM-marketplace-packages-page-size";
  private mmpmEnvVars: Map<string, string>;

  public ngOnInit(): void {
    this.setupTableData();

    if (!this.mmpmUtility.getCookie(this.mmpmMarketplacePaginatorCookieSize)) {
      this.mmpmUtility.setCookie(this.mmpmMarketplacePaginatorCookieSize, 10);
    }

    this.paginator.pageSize = Number(this.mmpmUtility.getCookie(this.mmpmMarketplacePaginatorCookieSize));
  }

  private setupTableData(): void {
    this.dataStore.mmpmEnvironmentVariables.subscribe((envVars: Map<string, string>) => this.mmpmEnvVars = envVars);

    this.dataStore.marketplacePackages.subscribe((allPackages: MagicMirrorPackage[]) => {
      this.dataStore.installedPackages.subscribe((installedPackages: MagicMirrorPackage[]) => {
        this.installedPackages = installedPackages;

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
      });
    });
  }

  private checkForInstallationConflicts(selectedPackages: MagicMirrorPackage[]): Promise<InstallationConflict> {
    let promise: Promise<InstallationConflict> = new Promise<InstallationConflict>((resolve, reject) => {

      let installationConflict: InstallationConflict = {
        matchesSelectedTitles: new Array<MagicMirrorPackage>(),
        matchesInstalledTitles: new Array<MagicMirrorPackage>()
      };

      this.dataStore.installedPackages.subscribe((installedPackages: MagicMirrorPackage[]) => {

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

      });
    });

    return promise;
  }

  private installPackages(selected: MagicMirrorPackage[]): void {
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
      this.dataStore.loadData();

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
          this.dataStore.loadData();

        } else {
          let dialogRef = this.dialog.open(
            InstallationConflictResolutionDialogComponent, {
              height: "50vh",
              width: "50vw",
              data: {
                matchesSelectedTitles: installationConflicts.matchesSelectedTitles,
                matchesInstalledTitles: installationConflicts.matchesInstalledTitles,
                magicmirrorRootDirectory: this.mmpmEnvVars.get('MMPM_MAGICMIRROR_ROOT')
              },
              disableClose: true
            });

          dialogRef.afterClosed().subscribe((toRemove: MagicMirrorPackage[]) => {
            if (!toRemove?.length) {
              return;
            }

            toRemove = [...toRemove, ...installationConflicts.matchesInstalledTitles];

            for (const remove of toRemove) {
              selected.splice(selected.findIndex((pkg: MagicMirrorPackage) => this.mmpmUtility.isSamePackage(pkg, remove)), 1);
            }

            console.log(selected);
            this.installPackages(selected);
            console.log('here')
          });
        }
      }).catch((error) => console.log(error));
    });
  }

  public onRefreshPackages(): void {
    this.snackbar.notify("Executing ... ");
    this.setupTableData();
    this.snackbar.notify("Refresh complete!");
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  public setPaginationCookie(pageEvent?: PageEvent): void {
    this.mmpmUtility.setCookie(this.mmpmMarketplacePaginatorCookieSize, pageEvent.pageSize);
  }
}
