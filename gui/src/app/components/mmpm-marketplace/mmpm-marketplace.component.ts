import { Component, ViewChild, ViewEncapsulation, OnInit } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { SelectionModel } from "@angular/cdk/collections";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSort } from "@angular/material/sort";
import { MatPaginator, PageEvent } from "@angular/material/paginator";
import { TooltipPosition } from "@angular/material/tooltip";
import { MagicMirrorPackage } from "src/app/interfaces/magic-mirror-package";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { TableUpdateNotifierService } from "src/app/services/table-update-notifier.service";
import { Subscription } from "rxjs";
import { TerminalStyledPopUpWindowComponent } from "src/app/components/terminal-styled-pop-up-window/terminal-styled-pop-up-window.component";
import { RenameModuleDirectoryDialogComponent } from "src/app/components/rename-module-directory-dialog/rename-module-directory-dialog.component";
import { DataStoreService } from "src/app/services/data-store.service";
import { MagicMirrorTableUtility } from "src/app/utils/magic-mirror-table-utlity";
import { CustomSnackbarComponent } from "src/app/components/custom-snackbar/custom-snackbar.component";
import { MMPMUtility } from "src/app/utils/mmpm-utility";

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
    private api: RestApiService,
    private dataStore: DataStoreService,
    public dialog: MatDialog,
    private notifier: TableUpdateNotifierService,
    private mSnackBar: MatSnackBar,
    private mmpmUtility: MMPMUtility
  ) {}

  public packages: MagicMirrorPackage[];
  public tableUtility: MagicMirrorTableUtility;

  private snackbar: CustomSnackbarComponent = new CustomSnackbarComponent(this.mSnackBar);
  private subscription: Subscription;
  private mmpmMarketplacePaginatorCookieSize: string = "MMPM-marketplace-page-size";


  dataSource: MatTableDataSource<MagicMirrorPackage>;
  selection = new SelectionModel<MagicMirrorPackage>(true, []);
  tooltipPosition: TooltipPosition[] = ["below"];

  snackbarSettings: object = { duration: 5000 };

  public ngOnInit(): void {
    this.setupTableData();
    this.subscription = this.notifier.getNotification().subscribe((_) => { this.setupTableData(); });

    if (!this.mmpmUtility.getCookie(this.mmpmMarketplacePaginatorCookieSize)) {
      this.mmpmUtility.setCookie(this.mmpmMarketplacePaginatorCookieSize, 10);
    }

    this.paginator.pageSize = Number(this.mmpmUtility.getCookie(this.mmpmMarketplacePaginatorCookieSize));
  }

  private setupTableData(): void {
    this.dataStore.getAllAvailablePackages().then((pkgs) => {
      this.packages = pkgs;
      this.selection = new SelectionModel<MagicMirrorPackage>(true, []);
      this.dataSource = new MatTableDataSource<MagicMirrorPackage>(this.packages);
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
      this.tableUtility = new MagicMirrorTableUtility(this.selection, this.dataSource, this.sort, this.dialog);
    }).catch((error) => {
      console.log(error);
    });
  }

  private _installModules(selected: MagicMirrorPackage[]) {
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
      this.notifier.triggerTableUpdate();
    }).catch((error) => { console.log(error); });
  }

  public onInstallModules(): void {
    if (this.selection.selected.length) {
      const selected = this.selection.selected;
      this.selection.clear();

      this.api.checkForInstallationConflicts(selected).then((result: string) => {
        result = JSON.parse(result);

        let dialogRef: any = null;

        if (!result["conflicts"].length) {
          this._installModules(selected);
        } else {

          dialogRef = this.dialog.open(
            RenameModuleDirectoryDialogComponent,
            this.mmpmUtility.basicDialogSettings(result["conflicts"])
          );

          dialogRef.afterClosed().subscribe((updatedModules: MagicMirrorPackage[]) => {
            selected.forEach((selectedModule, selectedIndex: number) => {
              updatedModules.forEach((updatedModule: MagicMirrorPackage, _: number) => {
                if (selectedModule.title === updatedModule.title) {
                  if ((updatedModule.directory.length)) {
                    selectedModule.directory = updatedModule.directory;
                  } else {
                    selected.splice(selectedIndex, 1);
                  }
                }
              });
            });

            if (selected.length) {
              this._installModules(selected);
            }
          });
        }
      }).catch((error) => { console.log(error); });
    }
  }

  public onRefreshModules(): void {
    this.snackbar.notify("Executing ... ");

    this.api.refreshModules().subscribe((_: any) => {
      this.snackbar.notify("Complete");
      this.notifier.triggerTableUpdate();
    });
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  public setPaginationCookie(pageEvent?: PageEvent): void {
    this.mmpmUtility.setCookie(this.mmpmMarketplacePaginatorCookieSize, pageEvent.pageSize);
  }
}
