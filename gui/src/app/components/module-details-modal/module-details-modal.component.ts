import { Component, OnInit, Inject } from "@angular/core";
import { MatDialogRef, MAT_DIALOG_DATA } from "@angular/material/dialog";

@Component({
  selector: "app-module-details-modal",
  templateUrl: "./module-details-modal.component.html",
  styleUrls: ["./module-details-modal.component.scss"]
})
export class ModuleDetailsModalComponent implements OnInit {

  constructor(
    private dialogRef: MatDialogRef<ModuleDetailsModalComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) { }

  ngOnInit(): void {
  }

  onNoClick() {
  }
}
