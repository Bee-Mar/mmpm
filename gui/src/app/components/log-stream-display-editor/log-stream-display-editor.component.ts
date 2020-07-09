import { Component, OnInit, Input } from '@angular/core';
import * as Cookie from "js-cookie";
import io from "socket.io-client";
import { RestApiService } from "src/app/services/rest-api.service";
import { URLS } from "src/app/utils/urls";

@Component({
  selector: 'app-log-stream-display-editor',
  templateUrl: './log-stream-display-editor.component.html',
  styleUrls: ['./log-stream-display-editor.component.scss']
})
export class LogStreamDisplayEditorComponent implements OnInit {

  constructor(
    private api: RestApiService,
  ) { }

  @Input() logStream: string;

  private mmpmEditorThemeCookie = "MMPM-editor-theme";

  public editor: any;
  public socket: any;
  public code: string = "";

  public editorOptions = {
    theme: Cookie.get(this.mmpmEditorThemeCookie) ?? "vs-dark"
  };

  public ngOnInit(): void {
    this.api.retrieve(URLS.GET.MAGICMIRROR.URI).then((uri: object) => {
      this.socket = io(`${uri["MMPM_MAGICMIRROR_URI"]}/mmpm`, {reconnection: true});
      this.socket.on(this.logStream, (data: any) => {
        this.code += `${data.notification}\n`;
        console.log(data)
      });
    }).catch((error) => console.log(error));
  }

  public onEditorInit(editor: any): void {
    this.editor = editor;
  }

}
