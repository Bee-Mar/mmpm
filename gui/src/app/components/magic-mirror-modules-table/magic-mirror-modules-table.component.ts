import { Component, ViewChild, Input } from "@angular/core";
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

const select = "select";
const category = "category";
const title = "title";
const repository = "repository";
const author = "author";
const description = "description";

@Component({
  selector: "app-magic-mirror-modules-table",
  styleUrls: ["./magic-mirror-modules-table.component.scss"],
  templateUrl: "./magic-mirror-modules-table.component.html"
})
export class MagicMirrorModulesTableComponent {
  @ViewChild(MatPaginator, { static: true }) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;
  @Input() url: string;

  ALL_PACKAGES: Array<MagicMirrorPackage>;

  constructor(
    private api: RestApiService,
    public dialog: MatDialog,
    private snackbar: MatSnackBar
  ) { }

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

  public ngOnInit(): void {
    this.retrieveModules();
  }

  private retrieveModules(): void {
    this.ALL_PACKAGES = new Array<MagicMirrorPackage>();
    this.paginator.pageSize = 10;

    this.api.getModules(`/${this.url}`).subscribe((packages) => {
      Object.keys(packages).forEach((_category) => {
        if (packages) {
          for (const pkg of packages[_category]) {
            this.ALL_PACKAGES.push({
              category: _category,
              title: pkg["Title"],
              description: pkg["Description"],
              author: pkg["Author"],
              repository: pkg["Repository"]
            });
          }
        }
      });

      this.selection = new SelectionModel<MagicMirrorPackage>(true, []);
      this.dataSource = new MatTableDataSource<MagicMirrorPackage>(
        this.ALL_PACKAGES
      );
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    });
  }

  public compare(
    a: number | string,
    b: number | string,
    ascending: boolean
  ): number {
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
    this.isAllSelected() ? this.selection.clear() : this.dataSource?.data.forEach((row) => this.selection.select(row));
  }

  public onInstallModules(): void {
    if (this.selection.selected.length) {
      this.api.modifyModules("/install-modules", this.selection.selected).subscribe((_) => {
        const dialogRef = this.dialog.open(LiveTerminalFeedDialogComponent, { width: "50vw", height: "50vh"});

        dialogRef.afterClosed().subscribe((_) => {
          this.retrieveModules();
          this.snackbar.open("Process complete", "Close", { duration: 3000 });
        })
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
      if (result) {
        this.api.addExternalModuleSource(result).subscribe((success) => {
          let message: any;

          if (success) {
            this.retrieveModules();
            message = `Successfully added '${externalSource.title}' to 'External Module Sources'`;
          } else {
            message = "Failed to add new source";
          }

          this.snackbar.open(message, "Close", { duration: 3000 });
        });
      }
    });
  }

  public onRemoveExternalSource(): void {
    if (this.selection.selected.length) {
      this.api.removeExternalModuleSource(this.selection.selected).subscribe((success) => {
        let message: any;

        if (success) {
          this.retrieveModules();
          message = "Successfully deleted external source(s)";
        } else {
          message = "Failed to remove external source(s)";
        }

        this.snackbar.open(message, "Close", { duration: 3000 });
      });
    }
  }

  public onRefreshModules(): void { }

  public onUninstallModules(): void {
    if (this.selection.selected.length) {
      this.api
        .modifyModules("/uninstall-modules", this.selection.selected)
        .subscribe((success) => {
          let message: any;

          if (success) {
            this.retrieveModules();
            message = "Successfully deleted module(s)";
          } else {
            message = "Failed to remove module(s)";
          }

          this.snackbar.open(message, "Close", { duration: 3000 });
        });
    }
  }

  public onUpdateModules(): void {
    if (this.selection.selected) {
      this.api.updateModules(this.selection.selected).subscribe((success) => {
        let message: any;

        if (success) {
          this.retrieveModules();
          message = "Successfully updated module(s)";
        } else {
          message = "Failed to update selected module(s)";
        }

        this.snackbar.open(message, "Close", { duration: 3000 });
      });
    }
  }

  public checkboxLabel(row?: MagicMirrorPackage): string {
    if (!row) {
      return `${this.isAllSelected() ? "select" : "deselect"} all`;
    }

    return `${
      this.selection.isSelected(row) ? "deselect" : "select"
      } row ${row.category + 1}`;
  }
}
