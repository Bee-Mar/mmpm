import { Component, OnInit } from "@angular/core";
import { MatDialogRef } from "@angular/material/dialog";
import { LiveTerminalFeedService } from "src/app/services/live-terminal-feed.service";
import { Observable, combineLatest } from "rxjs";

@Component({
  selector: "app-live-terminal-feed-dialog",
  templateUrl: "./live-terminal-feed-dialog.component.html",
  styleUrls: ["./live-terminal-feed-dialog.component.scss"]
})
export class LiveTerminalFeedDialogComponent implements OnInit {
  socket: any;
  streams: Array<Promise<object>> = new Array<Promise<object>>();
  outputStream: string = "";

  constructor(
    private dialogRef: MatDialogRef<LiveTerminalFeedDialogComponent>,
    private terminalFeed: LiveTerminalFeedService
  ) {}

  ngOnInit(): void {
    this.socket = this.terminalFeed.getSocket();

    this.socket.on("live-terminal-stream", (stream: any) => {
      this.outputStream += stream.data;
    });
  }

  onNoClick() {}
}
