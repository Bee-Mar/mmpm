import { Component, OnInit } from "@angular/core";
import { MatDialogRef } from "@angular/material/dialog";
import { Subject } from "rxjs";
import io from "socket.io-client";

@Component({
  selector: "app-live-terminal-feed-dialog",
  templateUrl: "./live-terminal-feed-dialog.component.html",
  styleUrls: ["./live-terminal-feed-dialog.component.scss"]
})
export class LiveTerminalFeedDialogComponent implements OnInit {
  socket: any;
  outputStream: string = "";

  constructor(private dialogRef: MatDialogRef<LiveTerminalFeedDialogComponent>) {}

  ngOnInit(): void {
    this.socket = this.getSocket();

    this.socket.on("live-terminal-stream", (stream: any) => {
      this.outputStream += stream.data;
    });
  }

  private getSocket() {
    return io(`http://${window.location.hostname}:7890`, {
      reconnection: true,
      transports: ["websocket", "polling"]
    });
  }

  onNoClick() {
    this.socket.disconnect();
  }
}
