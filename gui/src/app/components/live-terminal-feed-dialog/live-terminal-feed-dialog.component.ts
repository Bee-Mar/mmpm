import { Component, OnInit } from "@angular/core";
import { MatDialogRef } from "@angular/material/dialog";
import { LiveTerminalFeedService } from "src/app/services/live-terminal-feed.service";
import { Observable, Subject } from "rxjs";

@Component({
  selector: "app-live-terminal-feed-dialog",
  templateUrl: "./live-terminal-feed-dialog.component.html",
  styleUrls: ["./live-terminal-feed-dialog.component.scss"]
})
export class LiveTerminalFeedDialogComponent implements OnInit {
  //outputStream: Subject<any>;
  outputStream: string;

  constructor(
    private dialogRef: MatDialogRef<LiveTerminalFeedDialogComponent>,
    private terminalFeed: LiveTerminalFeedService
  ) {
    this.outputStream = "hello";

    // this.outputStream = <Subject<any>>terminalFeed.connect().map(
    //   (response: any): any => {
    //     return response;
    //   })
  }

  ngOnInit(): void {}

  onNoClick() {}
}
