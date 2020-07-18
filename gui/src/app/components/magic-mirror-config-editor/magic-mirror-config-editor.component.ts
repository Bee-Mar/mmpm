import { Component, OnInit } from "@angular/core";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { ConfirmationDialogComponent } from "src/app/components/confirmation-dialog/confirmation-dialog.component";
import { URLS } from "src/app/utils/urls";
import { DataStoreService } from "src/app/services/data-store.service";
import * as Cookie from "js-cookie";

interface FileCharacteristics {
  name: string;
  syntax: string;
  url: string;
  code: string;
}

@Component({
  selector: "app-magic-mirror-config-editor",
  templateUrl: "./magic-mirror-config-editor.component.html",
  styleUrls: ["./magic-mirror-config-editor.component.scss"]
})
export class MagicMirrorConfigEditorComponent implements OnInit {
  constructor(
    private dialog: MatDialog,
    private api: RestApiService,
    private snackbar: MatSnackBar,
    private dataStore: DataStoreService,
  ) {}

  private mmpmEditorThemeCookie = "MMPM-editor-theme";
  private mmpmEditorCurrentFileCookie = "MMPM-editor-current-file";

  public CONFIG_JS: number = 0;
  public CUSTOM_CSS: number = 1;
  public MMPM_ENV_VARS_JSON: number = 2;
  public fileIndex: number = Number(Cookie.get(this.mmpmEditorCurrentFileCookie)) ?? this.CONFIG_JS;

  public editor: any;
  public code: string = "";
  public fileSelection: Array<FileCharacteristics>;

  public editorOptions = {
    theme: Cookie.get(this.mmpmEditorThemeCookie) ?? "vs-dark"
  };

  public ngOnInit(): void {
    this.fileSelection = [
      {name: "config.js", syntax: "javascript", url: URLS.GET.MAGICMIRROR.CONFIG, code: ""},
      {name: "custom.css", syntax: "css", url: URLS.GET.MAGICMIRROR.CUSTOM_CSS, code: ""},
      {name: "mmpm-env.json", syntax: "json", url: URLS.GET.MMPM.ENVIRONMENT_VARS_FILE, code: ""},
    ];

    this.api.getFile(URLS.GET.MAGICMIRROR.CONFIG).then((fileContents) => {
      this.fileSelection[this.CONFIG_JS].code = fileContents;
      // this is genuinely stupid. I should just be able to access the code in
      // the template by using 'fileSelection[fileSelection].code'. There's
      // probably a better way for checking if the value is undefined, but I'll
      // fix that later
      if (this.fileIndex === this.CONFIG_JS) this.code = fileContents;
    }).catch((error) => {
      console.log(error);
    });

    this.api.getFile(URLS.GET.MAGICMIRROR.CUSTOM_CSS).then((fileContents) => {
      this.fileSelection[this.CUSTOM_CSS].code = fileContents;
      if (this.fileIndex === this.CUSTOM_CSS) this.code = fileContents;
    }).catch((error) => {
      console.log(error);
    });

    this.api.getFile(URLS.GET.MMPM.ENVIRONMENT_VARS_FILE).then((fileContents) => {
      this.fileSelection[this.MMPM_ENV_VARS_JSON].code = fileContents;
      if (this.fileIndex === this.MMPM_ENV_VARS_JSON) this.code = fileContents;
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
    this.code = this.fileSelection[this.fileIndex].code;
    monaco.editor.setModelLanguage(this.editor.getModel(), this.fileSelection[this.fileIndex].syntax);
  }

  public onSaveConfig(): void {
    const file: string = this.fileSelection[this.fileIndex]?.name;
    this.fileSelection[this.fileIndex].code = this.code;

    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        message: `The local version of ${file} will be overwritten`
      },
      disableClose: true
    });

    dialogRef.afterClosed().subscribe((yes) => {
      if (!yes) return;

      let url: string = this.fileSelection[this.fileIndex]?.url;

      this.api.updateMagicMirrorConfig(url, this.fileSelection[this.fileIndex]?.code).subscribe((success) => {
        const message: any = success ? `Successfully saved ${file}` : `Failed to save ${file}`;
        this.snackbar.open(message, "Close", { duration: 3000 });
        this.dataStore.retrieveMagicMirrorPackageData();
      });
    });
  }

  public onToggleTheme() {
    const newTheme = this.editorOptions.theme === "vs-dark" ? "vs-light" : "vs-dark";
    monaco.editor.setTheme(newTheme);
    this.editorOptions.theme = newTheme;
    Cookie.set(this.mmpmEditorThemeCookie, newTheme, {expires: 1825, path: ""});
  }

  public setFileIndexAndCookie(index: number = 0): void {
    this.fileIndex = index;
    this.code = this.fileSelection[index].code;
    monaco.editor.setModelLanguage(this.editor.getModel(), this.fileSelection[this.fileIndex].syntax);
    Cookie.set(this.mmpmEditorCurrentFileCookie, String(index), {expires: 1825, path: ""});
  }
}
