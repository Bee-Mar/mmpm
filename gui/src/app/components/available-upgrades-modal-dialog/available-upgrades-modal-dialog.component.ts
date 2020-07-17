import { Component, OnInit, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialog } from "@angular/material/dialog";
import { FormControl } from '@angular/forms';
import { MatListOption } from "@angular/material/list";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";
import { ConfirmationDialogComponent } from "src/app/components/confirmation-dialog/confirmation-dialog.component";
import { MatSnackBar } from "@angular/material/snack-bar";
import { CustomSnackbarComponent } from "src/app/components/custom-snackbar/custom-snackbar.component";
import { RestApiService } from "src/app/services/rest-api.service";
import { TerminalStyledPopUpWindowComponent } from "src/app/components/terminal-styled-pop-up-window/terminal-styled-pop-up-window.component";
import { MMPMUtility } from "src/app/utils/mmpm-utility";
import { DataStoreService } from "src/app/services/data-store.service";

@Component({
  selector: 'app-available-upgrades-modal-dialog',
  templateUrl: './available-upgrades-modal-dialog.component.html',
  styleUrls: ['./available-upgrades-modal-dialog.component.scss']
})
export class AvailableUpgradesModalDialogComponent implements OnInit {

  constructor(
    public dialog: MatDialog,
    private dialogRef: MatDialogRef<AvailableUpgradesModalDialogComponent>,
    private api: RestApiService,
    private mSnackBar: MatSnackBar,
    private mmpmUtility: MMPMUtility,
    private dataStore: DataStoreService,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) { }

  private snackbar: CustomSnackbarComponent = new CustomSnackbarComponent(this.mSnackBar);
  public choicesFormControl = new FormControl();

  ngOnInit(): void { }

  public upgradePackages(selection: MatListOption[]): void {
    let selectedPackages: Array<MagicMirrorPackage> = new Array<MagicMirrorPackage>();
    selection.forEach((selected) => selectedPackages.push(selected.value.value));
    const numPackages: number = selectedPackages.length;

    const confirmationDialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        message: `${numPackages} ${numPackages === 1 ? "package" : "packages"} will be upgraded, if available`
      },
      disableClose: true
    });

    confirmationDialogRef.afterClosed().subscribe((yes) => {
      if (!yes) {
        return;
      }

      let ids: Array<number> = this.mmpmUtility.saveProcessIds(selectedPackages, "Upgrading");

      this.snackbar.notify("Executing ...");

      this.api.packagesUpgrade(selectedPackages).then((fails) => {
        fails = JSON.parse(fails);

        if (fails.length) {
          this.dialog.open(TerminalStyledPopUpWindowComponent, this.mmpmUtility.basicDialogSettings(fails));
          this.snackbar.error(`Failed to upgrade ${fails.length} ${fails.length == 1 ? "package" : "packages"}`);
        } else {
          this.snackbar.success("Upgraded selected modules successfully!");
        }

        this.mmpmUtility.deleteProcessIds(ids);
        this.dataStore.loadData();
        this.dialogRef.close();

      }).catch((error) => console.log(error));
    });
  }
}
