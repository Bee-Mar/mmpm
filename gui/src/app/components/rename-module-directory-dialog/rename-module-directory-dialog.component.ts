import { Component, OnInit, Inject } from "@angular/core";
import { MatDialogRef, MAT_DIALOG_DATA } from "@angular/material/dialog";

@Component({
  selector: "app-rename-module-directory-dialog",
  templateUrl: "./rename-module-directory-dialog.component.html",
  styleUrls: ["./rename-module-directory-dialog.component.scss"]
})
export class RenameModuleDirectoryDialogComponent implements OnInit {
  constructor(
    private dialogRef: MatDialogRef<RenameModuleDirectoryDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) { }

  public ngOnInit(): void {}

  public onSubmitNewDirectoryNames(data: any): void {
    this.dialogRef.close(data);
  }
}
