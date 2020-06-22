import { Component, ViewChild, ViewEncapsulation, OnInit } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { SelectionModel } from "@angular/cdk/collections";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSort } from "@angular/material/sort";
import { MatPaginator, PageEvent } from "@angular/material/paginator";
import { MagicMirrorPackage } from "src/app/interfaces/magic-mirror-package";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { TableUpdateNotifierService } from "src/app/services/table-update-notifier.service";
import { Subscription } from "rxjs";
import { TerminalStyledPopUpWindowComponent } from "src/app/components/terminal-styled-pop-up-window/terminal-styled-pop-up-window.component";
import { RenamePackageDirectoryDialogComponent } from "src/app/components/rename-package-directory-dialog/rename-package-directory-dialog.component";
import { DataStoreService } from "src/app/services/data-store.service";
import { MagicMirrorTableUtility } from "src/app/utils/magic-mirror-table-utlity";
import { CustomSnackbarComponent } from "src/app/components/custom-snackbar/custom-snackbar.component";
import { MMPMUtility } from "src/app/utils/mmpm-utility";
import { ActiveProcessCountService } from "src/app/services/active-process-count.service";

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

  public packages: MagicMirrorPackage[];
  public tableUtility: MagicMirrorTableUtility;

  private snackbar: CustomSnackbarComponent = new CustomSnackbarComponent(this.mSnackBar);
  private subscription: Subscription;
  private mmpmMarketplacePaginatorCookieSize: string = "MMPM-marketplace-packages-page-size";

  dataSource: MatTableDataSource<MagicMirrorPackage>;
  selection = new SelectionModel<MagicMirrorPackage>(true, []);

  snackbarSettings: object = { duration: 5000 };

  public ngOnInit(): void {
    this.setupTableData();
    this.subscription = this.notifier.getNotification().subscribe((_) => this.setupTableData(true));

    if (!this.mmpmUtility.getCookie(this.mmpmMarketplacePaginatorCookieSize)) {
      this.mmpmUtility.setCookie(this.mmpmMarketplacePaginatorCookieSize, 10);
    }

    this.paginator.pageSize = Number(this.mmpmUtility.getCookie(this.mmpmMarketplacePaginatorCookieSize));
  }

  private setupTableData(refresh: boolean = false): void {
    this.dataStore.getAllAvailablePackages(refresh).then((allPackages: MagicMirrorPackage[]) => {
      this.dataStore.getAllInstalledPackages(refresh).then((installedPackages: MagicMirrorPackage[]) => {

        // removing all the packages that are currently installed from the list of available packages
        for (const installedPackage of installedPackages) {
          let index: number = allPackages.findIndex(
            (availablePackage: MagicMirrorPackage) =>
            availablePackage.repository === installedPackage.repository &&
            availablePackage.title === installedPackage.title &&
            availablePackage.author === installedPackage.author
          );

          if (index > -1) allPackages.splice(index, 1);
        }

        this.packages = allPackages;
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
      }).catch((error) => console.log(error));
    }).catch((error) => console.log(error));
  }

  private checkForInstallationConflicts(selectedPackages: MagicMirrorPackage[]): Promise<MagicMirrorPackage[]> {
    let promise = new Promise<MagicMirrorPackage[]>((resolve, reject) => {
      this.dataStore.getAllInstalledPackages().then((installedPackages: MagicMirrorPackage[]) => {

        let duplicates: Array<MagicMirrorPackage> = new Array<MagicMirrorPackage>();
        let existingPackages: Array<MagicMirrorPackage> = new Array<MagicMirrorPackage>();

        for (const selectedPackage of selectedPackages) {
          const index = this.tableUtility.findPackageInstalledWithSameName(
            selectedPackage,
            installedPackages
          );

          if (index !== -1) {
            existingPackages.push(installedPackages[index]);
            continue;
          }

          let dups = this.tableUtility.findDuplicateSelectedPackages(selectedPackages, selectedPackage.title);
          console.log(dups);

          if (!dups?.length) {
            continue;
          }

          //duplicates += dups;
        }

        resolve(duplicates);

      }).catch((error) => {
        console.log(error);
        reject(new Array<MagicMirrorPackage>());
      });
    });

    return promise;
  }

  private installModules(selected: MagicMirrorPackage[]) {
    let ids: Array<number> = this.tableUtility.saveProcessIds(
      selected,
      selected.length > 1 ? "[ Batch Installation ]" : "[ Installing ]"
    );

    this.api.installModules(selected).then((result: string) => {
      result = JSON.parse(result);

      const failures: Array<object> = result["failures"];
      const pkg = failures.length == 1 ? "package" : "packages";

      if (failures.length) {
        this.dialog.open(TerminalStyledPopUpWindowComponent, this.mmpmUtility.basicDialogSettings(failures));
        this.snackbar.error(`${failures.length} ${pkg} failed to install`);

      } else {
        this.snackbar.success("Installed successfully!");
      }

      this.tableUtility.deleteProcessIds(ids);
      this.notifier.triggerTableUpdate();

    }).catch((error) => console.log(error));
  }

  public onInstallModules(): void {
    if (this.selection.selected.length) {
      const selected = this.selection.selected;
      this.selection.clear();

      this.checkForInstallationConflicts(selected).then((duplicates: MagicMirrorPackage[]) => {
        console.log(duplicates);

        //if (!conflicts.length) {
        //  this.installModules(selected);
        //} else {

        //  let dialogRef = this.dialog.open(
        //    RenamePackageDirectoryDialogComponent,
        //    this.mmpmUtility.basicDialogSettings(result["conflicts"])
        //  );

        //  dialogRef.afterClosed().subscribe((updatedModules: MagicMirrorPackage[]) => {
        //    selected.forEach((selectedModule, selectedIndex: number) => {
        //      updatedModules.forEach((updatedModule: MagicMirrorPackage, _: number) => {
        //        if (selectedModule.title === updatedModule.title) {
        //          if ((updatedModule.directory.length)) {
        //            selectedModule.directory = updatedModule.directory;
        //          } else {
        //            selected.splice(selectedIndex, 1);
        //          }
        //        }
        //      });
        //    });

        //    if (selected.length) {
        //      this.installModules(selected);
        //    }
        //  });
        //}
      }).catch((error) => console.log(error));
    }
  }

  /*
  NOTE: this is broken simply because of the eventlet bug
  public onRefreshModules(): void {
    this.snackbar.notify("Executing ... ");

    this.api.refreshModules().then((_: any) => {
      this.snackbar.notify("Database refresh complete!");
      this.notifier.triggerTableUpdate();
    }).catch((error) => {
      console.log(error);
    });
  }
   */

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  public setPaginationCookie(pageEvent?: PageEvent): void {
    this.mmpmUtility.setCookie(this.mmpmMarketplacePaginatorCookieSize, pageEvent.pageSize);
  }
}
