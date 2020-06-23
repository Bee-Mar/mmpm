import { Component, OnInit, Inject } from "@angular/core";
import { MatDialogRef, MAT_DIALOG_DATA } from "@angular/material/dialog";

@Component({
  selector: "app-rename-package-directory-dialog",
  templateUrl: "./rename-package-directory-dialog.component.html",
  styleUrls: ["./rename-package-directory-dialog.component.scss"]
})
export class RenamePackageDirectoryDialogComponent implements OnInit {
  constructor(
    private dialogRef: MatDialogRef<RenamePackageDirectoryDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) { }

  public ngOnInit(): void {
    console.log(this.data);
  }

  public onSubmitNewDirectoryNames(): void {
    this.dialogRef.close(this.data);
  }
}
