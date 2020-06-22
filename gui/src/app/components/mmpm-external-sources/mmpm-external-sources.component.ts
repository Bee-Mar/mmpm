import { Component, ViewChild, OnInit } from "@angular/core";
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
import { DataStoreService } from "src/app/services/data-store.service";
import { MagicMirrorTableUtility } from "src/app/utils/magic-mirror-table-utlity";
import { CustomSnackbarComponent } from "src/app/components/custom-snackbar/custom-snackbar.component";
import { ExternalSourceRegistrationDialogComponent } from "src/app/components/external-source-registration-dialog/external-source-registration-dialog.component";
import { MMPMUtility } from "src/app/utils/mmpm-utility";
import { ActiveProcessCountService } from "src/app/services/active-process-count.service";

@Component({
  selector: "app-mmpm-external-sources",
  templateUrl: "./mmpm-external-sources.component.html",
  styleUrls: [
    "./mmpm-external-sources.component.scss",
    "../../shared-styles/shared-table-styles.scss"
  ]
})
export class MMPMExternalSourcesComponent implements OnInit {
  @ViewChild(MatPaginator, { static: true }) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;

  constructor(
    public dialog: MatDialog,
    private api: RestApiService,
    private dataStore: DataStoreService,
    private notifier: TableUpdateNotifierService,
    private mSnackBar: MatSnackBar,
    private mmpmUtility: MMPMUtility,
    private activeProcessService: ActiveProcessCountService,
  ) {}

  public packages: MagicMirrorPackage[];
  private snackbar: CustomSnackbarComponent = new CustomSnackbarComponent(this.mSnackBar);
  public tableUtility: MagicMirrorTableUtility;
  private subscription: Subscription;
  private mmpmExternalPackagesPageSizeCookie: string = "MMPM-external-packages-page-size";

  dataSource: MatTableDataSource<MagicMirrorPackage>;
  selection = new SelectionModel<MagicMirrorPackage>(true, []);
  tooltipPosition: TooltipPosition[] = ["below"];

  snackbarSettings: object = { duration: 5000 };

  public ngOnInit(): void {
    this.setupTableData();
    this.subscription = this.notifier.getNotification().subscribe((_) => { this.setupTableData(true); });

    if (!this.mmpmUtility.getCookie(this.mmpmExternalPackagesPageSizeCookie)) {
      this.mmpmUtility.setCookie(this.mmpmExternalPackagesPageSizeCookie, "10");
    }

    this.paginator.pageSize = Number(this.mmpmUtility.getCookie(this.mmpmExternalPackagesPageSizeCookie));
  }

  private setupTableData(refresh: boolean = false): void {
    this.dataStore.getAllExternalPackages(refresh).then((pkgs) => {
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

  public onAddExternalSources(): void {
    const dialogRef = this.dialog.open(ExternalSourceRegistrationDialogComponent, {
      minWidth: "60vw", disableClose: true
    });

    dialogRef.afterClosed().subscribe((newExternalPackage: MagicMirrorPackage) => {
      // the user may have exited without entering anything
      if (newExternalPackage) {
        let ids: Array<number> = new Array<number>();

        for (let pkg of this.selection.selected) {
          ids.push(this.activeProcessService.insertProcess({
            name: `Adding External Source ${pkg.title}`,
            startTime: Date().toString()
          }));
        }

        this.api.addExternalModuleSource(newExternalPackage).then((error) => {
          console.log(error["error"]);

          const message = error["error"] === "no_error" ?
            `Successfully added '${newExternalPackage.title}' to 'External Module Sources'` :
            "Failed to add new source";

          for (let id of ids) {
            this.activeProcessService.removeProcess(id);
          }
          this.notifier.triggerTableUpdate();
          this.snackbar.success(message);
        }).catch((error) => {
          console.log(error);
        });
      }
    });
  }

  public onRemoveExternalSource(): void {
    if (this.selection.selected.length) {
      this.snackbar.notify("Executing ... ");

      console.log(this.selection.selected);
      this.api.removeExternalModuleSource(this.selection.selected).then((unused) => {
        this.snackbar.success("Process complete!");
        this.notifier.triggerTableUpdate();
      }).catch((error) => {
        console.log(error);
      });
    }
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  public setPaginationCookie(pageEvent?: PageEvent): void {
    this.mmpmUtility.setCookie(this.mmpmExternalPackagesPageSizeCookie, pageEvent.pageSize);
  }
}
