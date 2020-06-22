import { Component, OnInit, Inject } from "@angular/core";
import { MatDialogRef, MAT_DIALOG_DATA } from "@angular/material/dialog";

@Component({
  selector: "app-package-details-modal",
  templateUrl: "./package-details-modal.component.html",
  styleUrls: ["./package-details-modal.component.scss"]
})
export class PackageDetailsModalComponent implements OnInit {

  constructor(
    private dialogRef: MatDialogRef<PackageDetailsModalComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) { }

  public ngOnInit(): void {
  }

  public onNoClick(): void {}
}
