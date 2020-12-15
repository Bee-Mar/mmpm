import { Component, OnInit } from '@angular/core';
import { MatDialogRef, MatDialog } from "@angular/material/dialog";
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
  ) { }

  private snackbar: CustomSnackbarComponent = new CustomSnackbarComponent(this.mSnackBar);
  public upgradeMagicMirror: boolean = false;
  public availableUpgrades: any;

  // dummy package for consistency in presentation
  public MagicMirror: MagicMirrorPackage = {
    title: "MagicMirror",
    author: "",
    repository: "",
    directory: "",
    description: "",
    category: "",
  };

  ngOnInit(): void {
    this.dataStore.upgradablePackages.subscribe((upgradable: any) => this.availableUpgrades = upgradable);
  }

  public upgradePackages(selection: MatListOption[]): void {
    let selectedPackages: Array<MagicMirrorPackage> = new Array<MagicMirrorPackage>();

    selection.forEach((selected) => {
      selected.value.title === "MagicMirror" ? this.upgradeMagicMirror = true : selectedPackages.push(selected.value);
    });

    const numPackages: number = selection.length;

    const confirmationDialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        message: `${numPackages} ${numPackages === 1 ? "package" : "packages"} will be upgraded, if available`
      },
      disableClose: true
    });

    confirmationDialogRef.afterClosed().subscribe((yes) => {
      if (!yes) {
        this.dialogRef.close();
        return;
      }

      if (selectedPackages.length) {
        let ids: Array<number> = this.mmpmUtility.saveProcessIds(selectedPackages, "Upgrading");

        this.snackbar.notify("Upgrading packages ...");

        this.api.packagesUpgrade(selectedPackages).then((fails) => {
          fails = JSON.parse(fails);

          if (fails.length) {
            this.dialog.open(TerminalStyledPopUpWindowComponent, this.mmpmUtility.basicDialogSettings(fails));
            this.snackbar.error(`Failed to upgrade ${fails.length} ${fails.length == 1 ? "package" : "packages"}`);
          } else {
            this.snackbar.success("Upgraded selected modules successfully!");
          }

          this.mmpmUtility.deleteProcessIds(ids);
          this.dataStore.retrieveMagicMirrorPackageData();
        }).catch((error) => console.log(error));
      }

      if (this.upgradeMagicMirror) {
        let ids: Array<number> = this.mmpmUtility.saveProcessIds([this.MagicMirror], "Upgrading");

        this.snackbar.notify("Upgrading MagicMirror ...");

        this.api.upgradeMagicMirror().then((error) => {

          if (error.error.length) {
            this.dialog.open(TerminalStyledPopUpWindowComponent, this.mmpmUtility.basicDialogSettings(error.error));
            this.snackbar.error("Failed to upgrade MagicMirror");
          } else {
            this.snackbar.success("Upgraded selected modules successfully!");
          }

          this.mmpmUtility.deleteProcessIds(ids);
          this.dataStore.retrieveMagicMirrorPackageData();
        }).catch((error) => console.log(error));
      }

      this.dialogRef.close();
    });
  }

  public toggleMagicMirror() {
    this.upgradeMagicMirror = !this.upgradeMagicMirror;
    console.log(this.upgradeMagicMirror);
  }
}
