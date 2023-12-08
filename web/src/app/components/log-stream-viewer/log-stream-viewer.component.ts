import {Component, OnInit} from '@angular/core';
import {io} from "socket.io-client";
import {get_cookie, set_cookie} from '@/utils/utils';
import {BaseAPI} from '@/services/api/base-api';
import {RingBuffer} from './ring-buffer';

@Component({
  selector: 'app-log-stream-viewer',
  templateUrl: './log-stream-viewer.component.html',
  styleUrls: ['./log-stream-viewer.component.scss']
})
export class LogStreamViewerComponent implements OnInit {
  constructor(private base_api: BaseAPI) {}

  // using a RingBuffer because we don't need to display ALL of the logs. It's
  // unlikely anyone will be scrolling back too far, and they can just
  // download the logs anyway
  public socket: any;
  public logs = new RingBuffer<string>(500); // limit the logs displayed the most recent 500 lines
  public font_size = 12;

  public ngOnInit(): void {
    if (!get_cookie("mmpm-log-stream-font-size")) {
      set_cookie("mmpm-log-stream-font-size", "12");
    }

    this.font_size = Number(get_cookie("mmpm-log-stream-font-size"));

    this.socket = io(`ws://localhost:6789`, {reconnection: true});

    this.socket.on("connect", () => {
      console.log("Connected to Socket.IO log server");
    });

    this.socket.on("logs", (data: string) => {
      this.logs.push(data);
    });
  }

  public set_font_size() {
    set_cookie("mmpm-log-stream-font-size", String(this.font_size));
  }

  public on_download() {
    this.base_api.get_zip_archive("logs/archive").then((archive: ArrayBuffer) => {
      const blob = new Blob([archive], {type: "application/zip"});
      const date = new Date();

      const file_name = `mmpm-logs-${date.getFullYear()}-${date.getMonth()}-${date.getDay()}.zip`;
      const url: string = URL.createObjectURL(blob);
      const a: HTMLAnchorElement = document.createElement("a") as HTMLAnchorElement;

      a.href = url;
      a.download = file_name;
      document.body.appendChild(a);
      a.click();

      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }
}
