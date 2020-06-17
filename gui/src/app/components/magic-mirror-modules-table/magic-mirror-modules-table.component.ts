import { Component, ViewChild, Input, ViewEncapsulation } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { SelectionModel } from "@angular/cdk/collections";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSort } from "@angular/material/sort";
import { MatPaginator } from "@angular/material/paginator";
import { TooltipPosition } from "@angular/material/tooltip";
import { ExternalSourceRegistrationDialogComponent } from "src/app/components/external-source-registration-dialog/external-source-registration-dialog.component";
import { MagicMirrorPackage } from "src/app/interfaces/magic-mirror-package";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { TableUpdateNotifierService } from "src/app/services/table-update-notifier.service";
import { Subscription } from "rxjs";
import { TerminalStyledPopUpWindowComponent } from "src/app/components/terminal-styled-pop-up-window/terminal-styled-pop-up-window.component";
import { ModuleDetailsModalComponent } from "src/app/components/module-details-modal/module-details-modal.component";
import { ActiveProcessCountService } from "src/app/services/active-process-count.service";
import { RenameModuleDirectoryDialogComponent } from "src/app/components/rename-module-directory-dialog/rename-module-directory-dialog.component";

const select = "select";
const category = "category";
const title = "title";
const repository = "repository";
const author = "author";
const description = "description";
const directory = "directory";

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
  private activeProcessSubsription: Subscription;

  constructor(
    private api: RestApiService,
    public dialog: MatDialog,
    private snackbar: MatSnackBar,
    private notifier: TableUpdateNotifierService,
    private activeProcessCount: ActiveProcessCountService
  ) {}

  ALL_PACKAGES: Array<MagicMirrorPackage>;
  maxDescriptionLength: number = 75;

  displayedColumns: string[] = [
    select,
    category,
    title,
    //repository,
    //author,
    description
  ];

  dataSource: MatTableDataSource<MagicMirrorPackage>;
  selection = new SelectionModel<MagicMirrorPackage>(true, []);
  tooltipPosition: TooltipPosition[] = ["below"];
  currentProcessCount: number = 0;

  snackbarSettings: object = { duration: 5000 };

  public ngOnInit(): void {
    this.retrieveModules();
    this.subscription = this.notifier.getNotification().subscribe((_) => { this.retrieveModules(); });
    this.activeProcessSubsription = this.activeProcessCount.getCurrentProcessCount().subscribe((count) => { this.currentProcessCount = count; });
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
    this.ALL_PACKAGES = new Array<MagicMirrorPackage>();
    this.paginator.pageSize = 10;

    this.api.retrieve(`/${this.url}`).subscribe((packages) => {
      Object.keys(packages).forEach((packageCategory) => {
        if (packages) {
          for (const pkg of packages[packageCategory]) {
            this.ALL_PACKAGES.push({
              category: packageCategory,
              title: pkg["title"],
              description: pkg["description"],
              author: pkg["author"],
              repository: pkg["repository"],
              directory: pkg["directory"] ?? ""
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

  private popUpMessage = (message: string) => {
    this.snackbar.open(message, "Close", this.snackbarSettings);
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
      const selected = this.selection.selected;
      this.selection.clear();
      console.log(selected);

      this.api.checkForInstallationConflicts(selected).subscribe((result: string) => {
        result = JSON.parse(result);
        const dialogRef = this.dialog.open(RenameModuleDirectoryDialogComponent, this.basicDialogSettings(result["conflicts"]));

        dialogRef.afterClosed().subscribe((updatedModules) => {
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

          if (!selected.length) return;
          this.executing();

          this.api.installModules(selected).subscribe((result: string) => {
            result = JSON.parse(result);
            const failures: Array<object> = result["failures"];

            const pkg = failures.length == 1 ? "package" : "packages";

            if (failures.length) {
              this.dialog.open(TerminalStyledPopUpWindowComponent, this.basicDialogSettings(failures));
              this.popUpMessage(`${failures.length} ${pkg} failed to install`);

            } else {
              this.popUpMessage("Installed successfully!");
            }
            this.notifier.triggerTableUpdate();
          });
        });
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
      description: "",
      directory: ""
    };

    const dialogRef = this.dialog.open(
      ExternalSourceRegistrationDialogComponent,
      {
        minWidth: "60vw",
        data: {
          externalSource
        },
        disableClose: true
      }
    );

    dialogRef.afterClosed().subscribe((result) => {
      // the user may have exited without entering anything
      if (result) {
        this.api.addExternalModuleSource(result).subscribe((error) => {
          console.log(error["error"]);
          const message = error["error"] === "no_error" ?
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
      this.executing();

      console.log(this.selection.selected);
      this.api.removeExternalModuleSource(this.selection.selected).subscribe((unused) => {
        this.complete();
        this.notifier.triggerTableUpdate();
      });
    }
  }

  public onRefreshModules(): void {
    this.executing();

    this.api.refreshModules().subscribe((unused) => {
      this.complete();
      this.notifier.triggerTableUpdate();
    });
  }

  public onUninstallModules(): void {
    if (this.selection.selected.length) {
      this.executing();
      const selected = this.selection.selected;
      this.selection.clear();

      this.api.uninstallModules(selected).subscribe((result: string) => {
        this.selection.clear();
        result = JSON.parse(result);
        const failures: Array<object> = result["failures"];

        if (failures.length) {
          const pkg = failures.length == 1 ? "package" : "packages";
          this.dialog.open(TerminalStyledPopUpWindowComponent, this.basicDialogSettings(failures));
          this.popUpMessage(`Failed to remove ${failures.length} ${pkg}`);

        } else {
          this.popUpMessage("Removed successfully!");
        }

        this.notifier.triggerTableUpdate();
      });
    }
  }

  public onUpgradeModules(): void {
    if (this.selection.selected) {
      this.executing();

      this.api.upgradeModules(this.selection.selected).subscribe((fails) => {
        fails = JSON.parse(fails);

        if (fails.length) {
          const pkg = fails.length == 1 ? "package" : "packages";
          this.dialog.open(TerminalStyledPopUpWindowComponent, this.basicDialogSettings(fails));
          this.popUpMessage(`Failed to upgrade ${fails.length} ${pkg}`);
        } else {
          this.popUpMessage("Upgraded selected modules successfully!");
        }
        this.notifier.triggerTableUpdate();
      });
    }
  }

  public checkboxLabel(row?: MagicMirrorPackage): string {
    if (!row) return `${this.isAllSelected() ? "select" : "deselect"} all`;
    return `${this.selection.isSelected(row) ? "deselect" : "select"} row ${row.category + 1}`;
  }

  public showModuleDetails(pkg: MagicMirrorPackage) {
    // since clicking on a cell selects the value, this actually sets the value
    // to state it was in at the time of selection
    this.selection.toggle(pkg);

    this.dialog.open(ModuleDetailsModalComponent, {
      width: "45vw",
      height: "50vh",
      disableClose: true,
      data: pkg
    });
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }
}
