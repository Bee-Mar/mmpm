import { Component, ViewChild, OnInit } from "@angular/core";
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
import { DataStoreService } from "src/app/services/data-store.service";
import { MagicMirrorTableUtility } from "src/app/utils/magic-mirror-table-utlity";
import { CustomSnackbarComponent } from "src/app/components/custom-snackbar/custom-snackbar.component";
import { ExternalSourceRegistrationDialogComponent } from "src/app/components/external-source-registration-dialog/external-source-registration-dialog.component";

const select = "select";
const category = "category";
const title = "title";
const description = "description";


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
    private api: RestApiService,
    private dataStore: DataStoreService,
    public dialog: MatDialog,
    private notifier: TableUpdateNotifierService,
    private mSnackBar: MatSnackBar
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
    this.setupTableData();
    this.subscription = this.notifier.getNotification().subscribe((_) => {
      this.dataStore.refreshAllExternalPackages().then((_) => {
      }).catch((error) => {
        console.log(error);
      });
    });
  }

  private setupTableData(): void {
    this.dataStore.getAllExternalPackages().then((pkgs) => {
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

  private complete = () => {
    this.snackbar.notify("Process complete");
  };

  private executing = () => {
    this.snackbar.notify("Process executing ...");
  };

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
          this.snackbar.success(message);
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

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }
}
