import { Component, OnInit } from "@angular/core";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSnackBar } from "@angular/material/snack-bar";
import * as Cookie from "js-cookie";

@Component({
  selector: "app-magic-mirror-config-editor",
  templateUrl: "./magic-mirror-config-editor.component.html",
  styleUrls: ["./magic-mirror-config-editor.component.scss"]
})
export class MagicMirrorConfigEditorComponent implements OnInit {
  editor: any;

  private mmpmEditorThemeCookie = "MMPM-editor-theme";

  constructor(private api: RestApiService, private snackbar: MatSnackBar) {}

  editorOptions = {
    theme: Cookie.get(this.mmpmEditorThemeCookie) ?? "vs-dark"
  };

  code = "";

  ngOnInit(): void {
    this.api.getMagicMirrorConfig().subscribe((fileContents) => { this.code = fileContents ?? ""; });
  }

  public ngOnDestroy(): void {
    if (this.editor) {
      this.editor.dispose();
    }
  }

  public onEditorInit(editor: any): void {
    this.editor = editor;
  }

  public onSaveMagicMirrorConfig(): void {
    this.api.updateMagicMirrorConfig(this.code).subscribe((success) => {
      const message: any = success
        ? "Successfully saved MagicMirror config"
        : "Failed to save MagicMirror config";

      this.snackbar.open(message, "Close", { duration: 3000 });
    });
  }

  public onToggleTheme() {
    const newTheme = this.editorOptions.theme === "vs-dark" ? "vs-light" : "vs-dark";
    monaco.editor.setTheme(newTheme);
    this.editorOptions.theme = newTheme;
    Cookie.set(this.mmpmEditorThemeCookie, newTheme, { expires: 7, path: ""});
  }
}
