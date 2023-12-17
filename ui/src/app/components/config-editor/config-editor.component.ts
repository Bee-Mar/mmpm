import { Component, HostListener, OnInit, ViewChild } from "@angular/core";
import { EditorComponent } from "ngx-monaco-editor-v2";
import { getCookie, setCookie } from "@/utils/utils";
import { ConfigFileAPI } from "@/services/api/config-file-api.service";
import { MessageService } from "primeng/api";
import { APIResponse } from "@/services/api/base-api";
import { SharedStoreService } from "@/services/shared-store.service";

interface FileContentsState {
  current: string;
  saved: string;
  language: string;
}

@Component({
  selector: "app-config-editor",
  templateUrl: "./config-editor.component.html",
  styleUrls: ["./config-editor.component.scss"],
  providers: [MessageService],
})
export class ConfigEditorComponent implements OnInit {
  constructor(
    private configFileApi: ConfigFileAPI,
    private store: SharedStoreService,
    private msg: MessageService,
  ) {}

  @ViewChild(EditorComponent, { static: false })
  public editor: EditorComponent;

  public file = getCookie("mmpm-config-editor-selected-file", "config.js");
  public fontSize = Number(getCookie("mmpm-config-editor-font-size", "12"));

  public state: { [key: string]: FileContentsState } = {
    "config.js": {
      current: "",
      saved: "",
      language: "javascript",
    },
    "mmpm-env.json": {
      current: "",
      saved: "",
      language: "json",
    },
    "custom.css": {
      current: "",
      saved: "",
      language: "css",
    },
  };

  public fileOptions = [
    {
      label: "config.js",
      icon: "fa-solid fa-code",
      command: () => {
        this.onSelectFile("config.js");
      },
    },
    {
      label: "mmpm-env.json",
      icon: "fa-solid fa-code",
      command: () => {
        this.onSelectFile("mmpm-env.json");
      },
    },
    {
      label: "custom.css",
      icon: "fa-solid fa-code",
      command: () => {
        this.onSelectFile("custom.css");
      },
    },
  ];

  public options = {
    language: "javascript",
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

  @HostListener("window:beforeunload", ["$event"])
  public beforeUnload($event: BeforeUnloadEvent) {
    if (this.state[this.file].current !== this.state[this.file].saved) {
      $event.returnValue = `You have unsaved changes made to ${this.file}. Are you sure you want to exit?`;
    }
  }

  public handleKeyDown(event: KeyboardEvent): void {
    if (event.ctrlKey && event.key === "s") {
      event.preventDefault();

      if (this.state[this.file].current !== this.state[this.file].saved) {
        this.onSaveFile();
      }
    }
  }

  public ngOnInit(): void {
    this.onSelectFile(this.file);
  }

  public onEditorInit(editor: EditorComponent): void {
    this.editor = editor;
  }

  public onSelectFile(file: string): void {
    this.file = file;

    setCookie("mmpm-config-editor-selected-file", this.file);

    if (!this.state[file].current) {
      this.configFileApi.getConfigFile(this.file).then((contents: string) => {
        this.state[file].current = this.state[file].saved = contents;
        this.setLanguage();
      });
    } else {
      this.setLanguage();
    }
  }

  private setLanguage() {
    this.options = Object.assign({}, this.options, { language: this.state[this.file].language });
  }

  public onSaveFile(): void {
    this.configFileApi.postConfigFile(this.file, this.state[this.file].current).then((response: APIResponse) => {
      if (response.code === 200) {
        this.state[this.file].saved = this.state[this.file].current;
        this.store.load();
        this.msg.add({ severity: "success", summary: "Save File", detail: `Saved ${this.file}` });
      } else {
        console.log(response.message);
        this.msg.add({ severity: "error", summary: "Save File", detail: response.message });
      }
    });
  }

  public onFontSizeChange(): void {
    setCookie("mmpm-config-editor-font-size", String(this.fontSize));
    this.options = Object.assign({}, this.options, { fontSize: this.fontSize });
  }
}
