import { Component, OnInit, Inject } from "@angular/core";
import { MatDialogRef, MAT_DIALOG_DATA, MatDialog } from "@angular/material/dialog";
//import { FormControl, Validators } from "@angular/forms";
import { ConfirmationDialogComponent } from "src/app/components/confirmation-dialog/confirmation-dialog.component";
import { SelectionModel } from "@angular/cdk/collections";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";

@Component({
  selector: "app-installation-conflict-resolution-dialog",
  templateUrl: "./installation-conflict-resolution-dialog.component.html",
  styleUrls: ["./installation-conflict-resolution-dialog.component.scss"]
})
export class InstallationConflictResolutionDialogComponent implements OnInit {
  constructor(
    private dialogRef: MatDialogRef<InstallationConflictResolutionDialogComponent>,
    public dialog: MatDialog,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  public selection = new SelectionModel<MagicMirrorPackage>(true, []);

  ngOnInit(): void {
    this.selection = new SelectionModel<MagicMirrorPackage>(true, []);
  }

  public onCancel(): void {
    const confirmationDialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        message: "The installation process will be cancelled"
      },
      disableClose: true
    });

    confirmationDialogRef.afterClosed().subscribe((yes) => {
      if (yes) this.dialogRef.close();
    });
  }

  public onSubmit(): void {
    const confirmationDialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        message: "The following will be installed"
      },
      disableClose: true
    });

    confirmationDialogRef.afterClosed().subscribe((yes) => {
      if (yes) this.dialogRef.close();
    });
  }

}
