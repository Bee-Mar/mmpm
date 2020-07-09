import { Component, OnInit } from "@angular/core";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { ConfirmationDialogComponent } from "src/app/components/confirmation-dialog/confirmation-dialog.component";
import { URLS } from "src/app/utils/urls";
import * as Cookie from "js-cookie";

@Component({
  selector: "app-magic-mirror-config-editor",
  templateUrl: "./magic-mirror-config-editor.component.html",
  styleUrls: ["./magic-mirror-config-editor.component.scss"]
})
export class MagicMirrorConfigEditorComponent implements OnInit {
  constructor(
    private dialog: MatDialog,
    private api: RestApiService,
    private snackbar: MatSnackBar
  ) {}

  private mmpmEditorThemeCookie = "MMPM-editor-theme";
  private mmpmEditorCurrentFileCookie = "MMPM-editor-current-file";
  private CONFIG_JS: number = 0;
  private CUSTOM_CSS: number = 1;

  public editor: any;
  public code: Array<string>;
  public fileIndex: number;

  public editorOptions = {
    theme: Cookie.get(this.mmpmEditorThemeCookie) ?? "vs-dark"
  };

  public ngOnInit(): void {
    this.fileIndex = Number(Cookie.get(this.mmpmEditorCurrentFileCookie)) ?? this.CONFIG_JS;
    this.code = new Array<string>();

    this.api.getFile(URLS.GET.MAGICMIRROR.CONFIG).then((fileContents) => {
      this.code[this.CONFIG_JS] = fileContents ?? "";
    }).catch((error) => {
      console.log(error);
    });

    this.api.getFile(URLS.GET.MAGICMIRROR.CUSTOM_CSS).then((fileContents) => {
      this.code[this.CUSTOM_CSS] = fileContents ?? "";
    }).catch((error) => {
      console.log(error);
    });
  }

  public ngOnDestroy(): void {
    if (this.editor) {
      this.editor.dispose();
    }
  }

  public onEditorInit(editor: any): void {
    this.editor = editor;
  }

  public onSaveConfig(): void {
    const file: string = this.fileIndex === this.CONFIG_JS ? "config.js" : "custom.css";

    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        message: `Your local version of ${file} will be overwritten`
      },
      disableClose: true
    });

    dialogRef.afterClosed().subscribe((yes) => {
      if (!yes) return;

      const url = this.fileIndex == this.CONFIG_JS ? URLS.POST.MAGICMIRROR.CONFIG : URLS.POST.MAGICMIRROR.CUSTOM_CSS;

      this.api.updateMagicMirrorConfig(url, this.code[this.fileIndex]).subscribe((success) => {
        const message: any = success ? `Successfully saved ${file}` : `Failed to save ${file}`;
        this.snackbar.open(message, "Close", { duration: 3000 });
      });
    });
  }

  public onToggleTheme() {
    const newTheme = this.editorOptions.theme === "vs-dark" ? "vs-light" : "vs-dark";
    monaco.editor.setTheme(newTheme);
    this.editorOptions.theme = newTheme;
    Cookie.set(this.mmpmEditorThemeCookie, newTheme, {expires: 7, path: ""});
  }

  private setFileIndexCookie(): void {
    Cookie.set(this.mmpmEditorCurrentFileCookie, String(this.fileIndex), {expires: 7, path: ""});
  }

  public loadConfigJs() {
    this.fileIndex = this.CONFIG_JS;
    monaco.editor.setModelLanguage(this.editor.getModel(), "javascript");
    this.setFileIndexCookie();
  }

  public loadCustomCss() {
    this.fileIndex = this.CUSTOM_CSS;
    monaco.editor.setModelLanguage(this.editor.getModel(), "css");
    this.setFileIndexCookie();
  }
}
