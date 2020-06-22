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
import { TerminalStyledPopUpWindowComponent } from "src/app/components/terminal-styled-pop-up-window/terminal-styled-pop-up-window.component";
import { DataStoreService } from "src/app/services/data-store.service";
import { MagicMirrorTableUtility } from "src/app/utils/magic-mirror-table-utlity";
import { CustomSnackbarComponent } from "src/app/components/custom-snackbar/custom-snackbar.component";
import { MMPMUtility } from "src/app/utils/mmpm-utility";
import { ActiveProcessCountService } from "src/app/services/active-process-count.service";

@Component({
  selector: "app-mmpm-local-packages",
  templateUrl: "./mmpm-local-packages.component.html",
  styleUrls: [
    "./mmpm-local-packages.component.scss",
    "../../shared-styles/shared-table-styles.scss"
  ]
})
export class MMPMLocalPackagesComponent implements OnInit {

  @ViewChild(MatPaginator, { static: true }) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;

  constructor(
    private api: RestApiService,
    private dataStore: DataStoreService,
    public dialog: MatDialog,
    private notifier: TableUpdateNotifierService,
    private mSnackBar: MatSnackBar,
    private mmpmUtility: MMPMUtility,
    private activeProcessService: ActiveProcessCountService
  ) {}

  public packages: MagicMirrorPackage[];
  public tableUtility: MagicMirrorTableUtility;

  private snackbar: CustomSnackbarComponent = new CustomSnackbarComponent(this.mSnackBar);
  private subscription: Subscription;
  private mmpmLocalPackagesPageSizeCookie: string = "MMPM-local-packages-page-size";

  dataSource: MatTableDataSource<MagicMirrorPackage>;
  selection = new SelectionModel<MagicMirrorPackage>(true, []);
  tooltipPosition: TooltipPosition[] = ["below"];

  snackbarSettings: object = { duration: 5000 };

  public ngOnInit(): void {
    this.setupTableData();
    this.subscription = this.notifier.getNotification().subscribe((_) => { this.setupTableData(true); });

    if (!this.mmpmUtility.getCookie(this.mmpmLocalPackagesPageSizeCookie)) {
      this.mmpmUtility.setCookie(this.mmpmLocalPackagesPageSizeCookie, "10");
    }

    this.paginator.pageSize = Number(this.mmpmUtility.getCookie(this.mmpmLocalPackagesPageSizeCookie));
  }

  private setupTableData(refresh: boolean = false): void {
    this.dataStore.getAllInstalledPackages(refresh).then((pkgs) => {
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

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  public onUninstallModules(): void {
    if (this.selection.selected.length) {
      let ids: Array<number> = new Array<number>();

      for (let pkg of this.selection.selected) {
        ids.push(this.activeProcessService.insertProcess({
          name: `Removing ${pkg.title}`,
          startTime: Date().toString()
        }));
      }

      this.snackbar.notify("Executing ...");
      const selected = this.selection.selected;

      this.selection.clear();

      this.api.uninstallModules(selected).then((result: string) => {
        this.selection.clear();
        result = JSON.parse(result);
        const failures: Array<object> = result["failures"];

        if (failures.length) {
          const pkg = failures.length == 1 ? "package" : "packages";
          this.dialog.open(TerminalStyledPopUpWindowComponent, this.mmpmUtility.basicDialogSettings(failures));
          this.snackbar.error(`Failed to remove ${failures.length} ${pkg}`);

        } else {
          this.snackbar.success("Removed successfully!");
        }

        for (let id of ids) {
          this.activeProcessService.removeProcess(id);
        }

        this.notifier.triggerTableUpdate();
      }).catch((error) => { console.log(error); });
    }
  }

  public onUpgradeModules(): void {
    if (this.selection.selected) {
      this.snackbar.notify("Executing ...");

      this.api.upgradeModules(this.selection.selected).then((fails) => {
        fails = JSON.parse(fails);

        if (fails.length) {
          const pkg = fails.length == 1 ? "package" : "packages";
          this.dialog.open(TerminalStyledPopUpWindowComponent, this.mmpmUtility.basicDialogSettings(fails));
          this.snackbar.error(`Failed to upgrade ${fails.length} ${pkg}`);
        } else {
          this.snackbar.success("Upgraded selected modules successfully!");
        }
        this.notifier.triggerTableUpdate();
      }).catch((error) => { console.log(error); });
    }
  }

  public setPaginationCookie(pageEvent?: PageEvent): void {
    this.mmpmUtility.setCookie(this.mmpmLocalPackagesPageSizeCookie, pageEvent.pageSize);
  }
}
