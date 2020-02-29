import { Component, OnInit } from "@angular/core";
import { RestApiService } from "src/app/services/rest-api.service";

@Component({
  selector: "app-magic-mirror-config-editor",
  templateUrl: "./magic-mirror-config-editor.component.html",
  styleUrls: ["./magic-mirror-config-editor.component.scss"]
})
export class MagicMirrorConfigEditorComponent implements OnInit {
  editor: any;

  constructor(private api: RestApiService) {}

  editorOptions = {
    theme: "vs-dark"
  };

  code = "";

  ngOnInit(): void {
    this.api.getMagicMirrorConfig().subscribe((file) => {
      this.code = file ?? "";
    });
  }

  ngOnDestroy() {
    if (this.editor) this.editor.dispose();
  }

  onEditorInit(editor: any): void {
    this.editor = editor;
  }
}
