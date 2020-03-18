import { Component, OnInit } from "@angular/core";
import { MatDialogRef } from "@angular/material/dialog";
import { LiveTerminalFeedService } from "src/app/services/live-terminal-feed.service";
import * as io from "socket.io-client";

@Component({
  selector: "app-live-terminal-feed-dialog",
  templateUrl: "./live-terminal-feed-dialog.component.html",
  styleUrls: ["./live-terminal-feed-dialog.component.scss"]
})
export class LiveTerminalFeedDialogComponent implements OnInit {
  outputStream: string;
  OUTPUT_STREAM: string = '/live-terminal-output-stream';

  socket: any;

  constructor(
    private dialogRef: MatDialogRef<LiveTerminalFeedDialogComponent>,
    private terminalFeed: LiveTerminalFeedService
  ) {
    this.outputStream = "hello";

  }

  ngOnInit(): void {
    console.log('Calling connect');
    //const socket = io.connect(`ws://0.0.0.0:7890/socket.io/${this.OUTPUT_STREAM}`);
    //console.log(`Connected: ${socket.connected}`);

    // socket.on('connect', (socket: any) => {
    //   socket.on(this.OUTPUT_STREAM, (data: any) => {
    //     console.log(data);
    //   })
    // });
  }

  onNoClick() {
    this.socket.close()
  }
}
