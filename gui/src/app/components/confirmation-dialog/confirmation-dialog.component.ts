import { Component, OnInit } from "@angular/core";
import {MatDialogRef } from "@angular/material/dialog";

@Component({
  selector: "app-confirmation-dialog",
  templateUrl: "./confirmation-dialog.component.html",
  styleUrls: ["./confirmation-dialog.component.scss"]
})
export class ConfirmationDialogComponent implements OnInit {
  constructor(private dialogRef: MatDialogRef<ConfirmationDialogComponent>) {}

  ngOnInit(): void {}

  onConfirm(confirmed: boolean): void {
    this.dialogRef.close(confirmed);
  }

  onNoClick() {
    this.dialogRef.close(false);
  }
}
