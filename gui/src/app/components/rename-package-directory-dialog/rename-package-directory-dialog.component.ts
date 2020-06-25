import { Component, OnInit, Inject } from "@angular/core";
import { MatDialogRef, MAT_DIALOG_DATA, MatDialog } from "@angular/material/dialog";
import { FormControl, Validators } from "@angular/forms";
import { ConfirmationDialogComponent } from "src/app/components/confirmation-dialog/confirmation-dialog.component";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";

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
    console.log(this.data);
  }

  public onSubmitNewDirectoryNames(): void {
    if (this.verifyUniqueDirectoryNames()) {
      this.dialogRef.close(this.data);
    }
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

  public verifyUniqueDirectoryNames(): boolean {

    let pkgs: Array<MagicMirrorPackage> = new Array<MagicMirrorPackage>();

    for (const key of Object.keys(this.data)) {
      for (const pkg of this.data[key]) {
        if(pkg) pkgs.push(pkg);
      }
    }

    this.data.matchesSelectedTitles.map((pkg: MagicMirrorPackage) => `${this.data.magicmirrorRootDirectory}/${pkg.directory}`);

    for (const pkg of pkgs) {
      if (pkgs.filter((p: MagicMirrorPackage) => p.directory === pkg.directory).length)
        return false;
    }

    return true;
  }

  public getErrorMessage(formControl: FormControl): string {
    if (formControl.hasError("required")) {
      return "You must enter a value";
    }
  }
}
