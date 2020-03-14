import { Component, OnInit, Inject } from "@angular/core";
import { MatDialogRef, MAT_DIALOG_DATA } from "@angular/material/dialog";

@Component({
  selector: "app-live-feed-dialog",
  templateUrl: "./live-feed-dialog.component.html",
  styleUrls: ["./live-feed-dialog.component.scss"]
})
export class LiveFeedDialogComponent implements OnInit {
  constructor(
    private dialogRef: MatDialogRef<LiveFeedDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  ngOnInit(): void {
  }
}
