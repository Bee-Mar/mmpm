import { Component, ViewChild, ViewEncapsulation, OnInit } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { SelectionModel } from "@angular/cdk/collections";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSort } from "@angular/material/sort";
import { MatPaginator } from "@angular/material/paginator";
import { TooltipPosition } from "@angular/material/tooltip";
import { MagicMirrorPackage } from "src/app/interfaces/magic-mirror-package";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { TableUpdateNotifierService } from "src/app/services/table-update-notifier.service";
import { Subscription } from "rxjs";
import { TerminalStyledPopUpWindowComponent } from "src/app/components/terminal-styled-pop-up-window/terminal-styled-pop-up-window.component";
import { RenameModuleDirectoryDialogComponent } from "src/app/components/rename-module-directory-dialog/rename-module-directory-dialog.component";
import { DataStoreService } from "src/app/services/data-store.service";
import { MagicMirrorTableUtility, fillMagicMirrorPackageArray } from "src/app/utils/magic-mirror-table-utlity";
import { CustomSnackbarComponent } from "src/app/components/custom-snackbar/custom-snackbar.component";
import { URL } from "src/app/utils/urls";

const select = "select";
const category = "category";
const title = "title";
const description = "description";

@Component({
  selector: "app-mmpmmarketplace",
  templateUrl: "./mmpmmarketplace.component.html",
  styleUrls: ["./mmpmmarketplace.component.scss"],
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
  ) {}

  public packages: MagicMirrorPackage[];
  private snackbar: CustomSnackbarComponent = new CustomSnackbarComponent(this.mSnackBar);
  public tableUtility: MagicMirrorTableUtility;
  private subscription: Subscription;

  maxDescriptionLength: number = 75;

  displayedColumns: string[] = [
    select,
    category,
    title,
    description
  ];

  dataSource: MatTableDataSource<MagicMirrorPackage>;
  selection = new SelectionModel<MagicMirrorPackage>(true, []);
  tooltipPosition: TooltipPosition[] = ["below"];

  snackbarSettings: object = { duration: 5000 };

  public ngOnInit(): void {
    this.retrieveModules();
    this.subscription = this.notifier.getNotification().subscribe((_) => { this.retrieveModules(); });
    this.paginator.pageSize = 10;
  }

  private basicDialogSettings(data?: any): object {
    return data ? {
      width: "75vw",
      height: "75vh",
      disableClose: true,
      data
    } : {
      width: "75vw",
      height: "75vh",
      disableClose: true
    };
  }

  private retrieveModules(): void {
    this.api.retrieve(URL.ALL_AVAILABLE_MODULES).then((data) => {
      this.packages = fillMagicMirrorPackageArray(data);
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
        this.dialog.open(TerminalStyledPopUpWindowComponent, this.basicDialogSettings(failures));
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
            this.basicDialogSettings(result["conflicts"])
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
}
