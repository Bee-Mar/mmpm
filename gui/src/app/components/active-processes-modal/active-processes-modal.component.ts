import { Component, OnInit, Inject } from "@angular/core";
import { MatDialogRef, MAT_DIALOG_DATA } from "@angular/material/dialog";

@Component({
  selector: "app-active-processes-modal",
  templateUrl: "./active-processes-modal.component.html",
  styleUrls: ["./active-processes-modal.component.scss"]
})
export class ActiveProcessesModalComponent implements OnInit {
  constructor(
    private dialogRef: MatDialogRef<ActiveProcessesModalComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) { }

  public ngOnInit(): void {}

  public ngOnDestroy(): void {}
}

