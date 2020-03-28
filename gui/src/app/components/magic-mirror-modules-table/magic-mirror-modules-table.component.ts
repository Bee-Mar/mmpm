import { Component, ViewChild, Input, ViewEncapsulation } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { SelectionModel } from "@angular/cdk/collections";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSort } from "@angular/material/sort";
import { MatPaginator } from "@angular/material/paginator";
import { TooltipPosition } from "@angular/material/tooltip";
import { ExternalSourceRegistrationDialogComponent } from "src/app/components/external-source-registration-dialog/external-source-registration-dialog.component";
import { LiveTerminalFeedDialogComponent } from "src/app/components/live-terminal-feed-dialog/live-terminal-feed-dialog.component";
import { MagicMirrorPackage } from "src/app/interfaces/magic-mirror-package";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { TableUpdateNotifierService } from "src/app/services/table-update-notifier.service";
import { Subscription } from "rxjs";

const select = "select";
const category = "category";
const title = "title";
const repository = "repository";
const author = "author";
const description = "description";

@Component({
  selector: "app-magic-mirror-modules-table",
  styleUrls: ["./magic-mirror-modules-table.component.scss"],
  templateUrl: "./magic-mirror-modules-table.component.html",
  encapsulation: ViewEncapsulation.None,
})
export class MagicMirrorModulesTableComponent {
  @ViewChild(MatPaginator, { static: true }) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;
  @Input() url: string;

  private subscription: Subscription;

  constructor(
    private api: RestApiService,
    public dialog: MatDialog,
    private snackbar: MatSnackBar,
    private notifier: TableUpdateNotifierService
  ) {}

  ALL_PACKAGES: Array<MagicMirrorPackage>;
  maxDescriptionLength: number = 70;

  displayedColumns: string[] = [
    select,
    category,
    title,
    repository,
    author,
    description
  ];

  dataSource: MatTableDataSource<MagicMirrorPackage>;
  selection = new SelectionModel<MagicMirrorPackage>(true, []);
  tooltipPosition: TooltipPosition[] = ["below"];

  liveTerminalFeedDialogSettings: object = {
    width: "75vw",
    height: "75vh"
  };

  snackbarSettings: object = { duration: 3000 };

  public ngOnInit(): void {
    this.retrieveModules();
    this.subscription = this.notifier.getNotification().subscribe((unused) => { this.retrieveModules(); });
  }

  private retrieveModules(): void {
    this.ALL_PACKAGES = new Array<MagicMirrorPackage>();
    this.paginator.pageSize = 10;

    this.api.basicGet(`/${this.url}`).subscribe((packages) => {
      Object.keys(packages).forEach((packageCategory) => {
        if (packages) {
          for (const pkg of packages[packageCategory]) {
            this.ALL_PACKAGES.push({
              category: packageCategory,
              title: pkg["Title"],
              description: pkg["Description"],
              author: pkg["Author"],
              repository: pkg["Repository"]
            });
          }
        }
      });

      this.selection = new SelectionModel<MagicMirrorPackage>(true, []);
      this.dataSource = new MatTableDataSource<MagicMirrorPackage>(this.ALL_PACKAGES);
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    });
  }

  private complete = () => {
    this.snackbar.open("Process complete", "Close", this.snackbarSettings);
  };

  private executing = () => {
    this.snackbar.open("Process executing ...", "Close", this.snackbarSettings);
  };

  public compare(a: number | string, b: number | string, ascending: boolean): number {
    return (a < b ? -1 : 1) * (ascending ? 1 : -1);
  }

  public onSort(sort: MatSort) {
    const data = this.ALL_PACKAGES.slice();

    if (!sort.active || sort.direction === "") {
      this.ALL_PACKAGES = data;
      return;
    }

    this.ALL_PACKAGES = data.sort((a, b) => {
      const ascending = sort.direction === "asc";
      switch (sort.active) {
        case category:
          return this.compare(a.category, b.category, ascending);
        case title:
          return this.compare(a.title, b.title, ascending);
        case author:
          return this.compare(a.author, b.author, ascending);
        default:
          return 0;
      }
    });
  }

  public searchFilter(event: Event): void {
    const filterValue = (event.target as HTMLInputElement).value;
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }

  public isAllSelected(): boolean {
    return this.dataSource?.data.length === this.selection.selected.length;
  }

  public toggleSelectAll(): void {
    this.isAllSelected() ? this.selection.clear() : this.dataSource?.data.forEach((row) => { this.selection.select(row); });
  }

  public onInstallModules(): void {
    if (this.selection.selected.length) {

      this.dialog.open(LiveTerminalFeedDialogComponent, this.liveTerminalFeedDialogSettings);
      this.executing();

      this.api.modifyModules("/install-modules", this.selection.selected).subscribe((ununsed) => {
        this.complete();
        this.notifier.triggerTableUpdate();
      });
    }
  }

  public onAddExternalSources(): void {
    let externalSource: MagicMirrorPackage;

    externalSource = {
      title: "",
      author: "",
      repository: "",
      category: "External Module Sources",
      description: ""
    };

    const dialogRef = this.dialog.open(
      ExternalSourceRegistrationDialogComponent,
      {
        minWidth: "60vw",
        data: {
          externalSource
        }
      }
    );

    dialogRef.afterClosed().subscribe((result) => {
      // the user may have exited without entering anything
      if (result) {
        this.api.addExternalModuleSource(result).subscribe((success) => {

          const message = success ?
            `Successfully added '${externalSource.title}' to 'External Module Sources'` :
            "Failed to add new source";

          this.notifier.triggerTableUpdate();
          this.snackbar.open(message, "Close", this.snackbarSettings);
        });
      }
    });
  }

  public onRemoveExternalSource(): void {
    if (this.selection.selected.length) {

      this.dialog.open(LiveTerminalFeedDialogComponent, this.liveTerminalFeedDialogSettings);
      this.executing();

      this.api.removeExternalModuleSource(this.selection.selected).subscribe((unused) => {
        this.complete();
        this.notifier.triggerTableUpdate();
      });
    }
  }

  public onRefreshModules(): void {
    this.dialog.open(LiveTerminalFeedDialogComponent, this.liveTerminalFeedDialogSettings);
    this.executing();

    this.api.refreshModules().subscribe((unused) => {
      this.complete();
      this.notifier.triggerTableUpdate();
    });
  }

  public onUninstallModules(): void {
    if (this.selection.selected.length) {
      this.dialog.open(LiveTerminalFeedDialogComponent, this.liveTerminalFeedDialogSettings);
      this.executing();

      this.api.modifyModules("/uninstall-modules", this.selection.selected).subscribe((unused) => {
        this.complete();
        this.notifier.triggerTableUpdate();
      });
    }
  }

  public onUpgradeModules(): void {
    if (this.selection.selected) {
      this.dialog.open(LiveTerminalFeedDialogComponent, this.liveTerminalFeedDialogSettings);
      this.executing();

      this.api.upgradeModules(this.selection.selected).subscribe((unused) => {
        this.complete();
        this.notifier.triggerTableUpdate();
      });
    }
  }

  public checkboxLabel(row?: MagicMirrorPackage): string {
    if (!row) return `${this.isAllSelected() ? "select" : "deselect"} all`;
    return `${this.selection.isSelected(row) ? "deselect" : "select"} row ${row.category + 1}`;
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }
}
