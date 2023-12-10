import {Component, OnInit, ViewChild} from '@angular/core';
import {EditorComponent} from 'ngx-monaco-editor-v2';
import {get_cookie, set_cookie} from '@/utils/utils';
import {ConfigFileAPI} from '@/services/api/config-file-api.service';
import {MessageService} from 'primeng/api';
import {APIResponse} from '@/services/api/base-api';

interface FileContentsState {
  current: string;
  saved: string;
  language: string;
}

@Component({
  selector: 'app-config-editor',
  templateUrl: './config-editor.component.html',
  styleUrls: ['./config-editor.component.scss'],
  providers: [MessageService]
})
export class ConfigEditorComponent implements OnInit {
  constructor(private config_file_api: ConfigFileAPI) {}

  @ViewChild(EditorComponent, {static: false})
  public editor: EditorComponent;

  public file = "config.js";
  public font_size = Number(get_cookie("mmpm-config-editor-font-size", "12"));

  public state: {[key: string]: FileContentsState;} = {
    "config.js": {
      current: "",
      saved: "",
      language: "javascript"
    },
    "mmpm-env.json": {
      current: "",
      saved: "",
      language: "json"
    },
    "custom.css": {
      current: "",
      saved: "",
      language: "css"
    }
  };

  public file_options = [
    {
      label: "config.js",
      icon: "fa-solid fa-code",
      command: () => {
        this.on_select_file("config.js");
      }
    },
    {
      label: "mmpm-env.json",
      icon: "fa-solid fa-code",
      command: () => {
        this.on_select_file("mmpm-env.json");
      }
    },
    {
      label: "custom.css",
      icon: "fa-solid fa-code",
      command: () => {
        this.on_select_file("custom.css");
      }
    },
  ];

  public options = {
    language: "javascript",
    theme: "vs-dark",
    scrollBeyondLastLine: false,
    fontSize: this.font_size,
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
    this.on_select_file(this.file);
  }

  public on_editor_init(editor: any): void {
    this.editor = editor;
  }

  public on_theme_change(event: any): void {
    this.options.theme = event.target;
  }

  public on_select_file(file: string): void {
    this.file = file;

    if (!this.state[file].current) {
      this.config_file_api.get_config_file(this.file).then((contents: string) => {
        this.state[file].current = this.state[file].saved = contents;
        this.set_language();
      });
    } else {
      this.set_language();
    }
  }

  private set_language() {
    this.options = Object.assign({}, this.options, {language: this.state[this.file].language});
  }

  public on_save_file(): void {
    this.config_file_api.post_config_file(this.file, this.state[this.file].current).then((response: APIResponse) => {
      if (response.code === 200) {
        this.state[this.file].saved = this.state[this.file].current;
      } else {
        console.log(response.message);
      }
    });
  }

  public on_font_size_change(): void {
    set_cookie("mmpm-config-editor-font-size", String(this.font_size));
    this.options = Object.assign({}, this.options, {fontSize: this.font_size});
  }

}
