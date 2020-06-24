import { Component, OnInit, Inject } from "@angular/core";
import { MatDialogRef, MAT_DIALOG_DATA, MatDialog } from "@angular/material/dialog";
import { FormControl, Validators } from "@angular/forms";
import { ConfirmationDialogComponent } from "src/app/components/confirmation-dialog/confirmation-dialog.component";

@Component({
  selector: "app-rename-package-directory-dialog",
  templateUrl: "./rename-package-directory-dialog.component.html",
  styleUrls: ["./rename-package-directory-dialog.component.scss"]
})
export class RenamePackageDirectoryDialogComponent implements OnInit {
  constructor(
    private dialogRef: MatDialogRef<RenamePackageDirectoryDialogComponent>,
    public dialog: MatDialog,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) { }

  public packageDirectoryFormControl = new FormControl("", [Validators.required]);

  public ngOnInit(): void {
    console.log(this.data.installationConflicts);
  }

  public onSubmitNewDirectoryNames(): void {
    this.dialogRef.close(this.data);
  }

  public onCancel(): void {
    const confirmationDialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        message: "The installation process will be cancelled."
      },
      disableClose: true
    });

    confirmationDialogRef.afterClosed().subscribe((response) => {
      if (response) {
        this.dialogRef.close();
      }
    });
  }

  public verifyUniqueDirectoryNames(): boolean {

    return true;
  }

  public getErrorMessage(formControl: FormControl): string {
    if (formControl.hasError("required")) {
      return "You must enter a value";
    }
  }
}
