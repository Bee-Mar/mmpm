import {Component, OnDestroy, OnInit, ViewChild} from "@angular/core";
import {io} from "socket.io-client";
import {getCookie, setCookie} from "@/utils/utils";
import {BaseAPI} from "@/services/api/base-api";
import {EditorComponent} from "ngx-monaco-editor-v2";

@Component({
  selector: "app-log-stream-viewer",
  templateUrl: "./log-stream-viewer.component.html",
  styleUrls: ["./log-stream-viewer.component.scss"],
})
export class LogStreamViewerComponent implements OnInit, OnDestroy {
  constructor(private base_api: BaseAPI) {}

  @ViewChild(EditorComponent, {static: false})
  public editor: EditorComponent;

  public socket: any;
  public logs = "";
  public fontSize = Number(getCookie("mmpm-log-stream-font-size", "12"));

  public options = {
    language: "text",
    readOnly: true,
    theme: "vs-dark",
    scrollBeyondLastLine: false,
    fontSize: this.fontSize,
    minimap: {
      enabled: false,
    },
    scrollbar: {
      useShadows: true,
      verticalHasArrows: false,
      horizontalHasArrows: false,
      vertical: "visible",
      verticalScrollbarSize: 12,
      horizontalScrollbarSize: 12,
      arrowSize: 30,
    },
    automaticLayout: true,
  };

  public ngOnInit(): void {
    this.fontSize = Number(getCookie("mmpm-log-stream-font-size", "12"));

    this.socket = io(`ws://localhost:6789`, {reconnection: true});

    this.socket.on("connect", () => {
      console.log("Connected to Socket.IO log server");
    });

    this.socket.on("connect_error", () => {
      console.log("Failed to connect to MMPM Log Server ");
    });

    this.socket.on("logs", (data: string) => {
      this.logs += data + "\n\n";
    });
  }

  public ngOnDestroy(): void {
    if (this.socket.connected) {
      this.socket.disconnect();
    }
  }

  public onEditorInit(editor: any): void {
    this.editor = editor;
  }

  public onFontSizeChange(): void {
    setCookie("mmpm-log-stream-font-size", String(this.fontSize));
    this.options = Object.assign({}, this.options, {fontSize: this.fontSize});
  }

  public onDownload() {
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
