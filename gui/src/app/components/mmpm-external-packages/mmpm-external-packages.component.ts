import { Component, ViewChild, OnInit } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { SelectionModel } from "@angular/cdk/collections";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSort } from "@angular/material/sort";
import { MatPaginator, PageEvent } from "@angular/material/paginator";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { Subscription } from "rxjs";
import { DataStoreService } from "src/app/services/data-store.service";
import { MagicMirrorTableUtility } from "src/app/utils/magic-mirror-table-utlity";
import { CustomSnackbarComponent } from "src/app/components/custom-snackbar/custom-snackbar.component";
import { ExternalPackageRegistrationDialogComponent } from "src/app/components/external-package-registration-dialog/external-package-registration-dialog.component";
import { MMPMUtility } from "src/app/utils/mmpm-utility";
import { ConfirmationDialogComponent } from "src/app/components/confirmation-dialog/confirmation-dialog.component";

@Component({
  selector: "app-mmpm-external-packages",
  templateUrl: "./mmpm-external-packages.component.html",
  styleUrls: [
    "./mmpm-external-packages.component.scss",
    "../../shared-styles/shared-table-styles.scss"
  ],
})
export class MMPMExternalPackagesComponent implements OnInit {
  @ViewChild(MatPaginator, { static: true }) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;

  constructor(
    public dialog: MatDialog,
    private dataStore: DataStoreService,
    private api: RestApiService,
    private mSnackBar: MatSnackBar,
    private mmpmUtility: MMPMUtility,
  ) {}

  public packages: MagicMirrorPackage[];
  private snackbar: CustomSnackbarComponent = new CustomSnackbarComponent(this.mSnackBar);
  public tableUtility: MagicMirrorTableUtility;
  private subscription: Subscription;
  private mmpmExternalPackagesPageSizeCookie: string = "MMPM-external-packages-page-size";

  dataSource: MatTableDataSource<MagicMirrorPackage>;
  selection = new SelectionModel<MagicMirrorPackage>(true, []);

  snackbarSettings: object = { duration: 5000 };

  public ngOnInit(): void {
    this.setupTableData();

    if (!this.mmpmUtility.getCookie(this.mmpmExternalPackagesPageSizeCookie)) {
      this.mmpmUtility.setCookie(this.mmpmExternalPackagesPageSizeCookie, "10");
    }

    this.paginator.pageSize = Number(this.mmpmUtility.getCookie(this.mmpmExternalPackagesPageSizeCookie));
  }

  private setupTableData(): void {
    this.dataStore.externalPackages.subscribe((pkgs) => {
      this.packages = pkgs;
      this.selection = new SelectionModel<MagicMirrorPackage>(true, []);
      this.dataSource = new MatTableDataSource<MagicMirrorPackage>(this.packages);
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
      this.tableUtility = new MagicMirrorTableUtility(this.selection, this.dataSource, this.sort, this.dialog);
    });
  }

  public onAddExternalPackage(): void {
    const dialogRef = this.dialog.open(ExternalPackageRegistrationDialogComponent, {
      minWidth: "60vw", disableClose: true
    });

    dialogRef.afterClosed().subscribe((newExternalPackage: MagicMirrorPackage) => {
      // the user may have exited without entering anything
      if (!newExternalPackage?.title?.length) {
        dialogRef.close();
        return;
      }

      const confirmationDialogRef = this.dialog.open(ConfirmationDialogComponent, {
        data: {
          message: `${newExternalPackage.title} will be added to the database`
        },
        disableClose: true
      });

      confirmationDialogRef.afterClosed().subscribe((yes) => {
        if (!yes) {
          return;
        }

        let ids: Array<number> = this.mmpmUtility.saveProcessIds(this.selection.selected, "Adding External Source");

        this.api.addExternalPackage(newExternalPackage).then((error) => {
          console.log(error["error"]);

          const message = error["error"] === "no_error" ?
            `Successfully added '${newExternalPackage.title}' to 'External Packages'` :
            "Failed to add new source";

          this.mmpmUtility.deleteProcessIds(ids);
          this.dataStore.loadData(false);
          this.snackbar.success(message);
        }).catch((error) => console.log(error));
      });

    });
  }

  public onRemoveExternalPackage(): void {
    const confirmationDialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        message: "The selected external packages will be removed from the database"
      },
      disableClose: true
    });

    confirmationDialogRef.afterClosed().subscribe((yes) => {
      if (!yes) {
        return;
      }

      if (this.selection.selected.length) {
        this.snackbar.notify("Executing ... ");

        this.api.removeExternalPackage(this.selection.selected).then((_) => {
          this.dataStore.loadData();
          this.snackbar.success("Process complete!");
        }).catch((error) => {
          console.log(error);
        });
      }
    });
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  public setPaginationCookie(pageEvent?: PageEvent): void {
    this.mmpmUtility.setCookie(this.mmpmExternalPackagesPageSizeCookie, pageEvent.pageSize);
  }
}
