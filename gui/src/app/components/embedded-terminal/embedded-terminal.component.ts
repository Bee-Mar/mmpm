import { Component, OnInit, ViewChild, AfterViewInit } from "@angular/core";
import { NgTerminal } from "ng-terminal";
import { AttachAddon } from "xterm-addon-attach";

interface IAttachOptions {
  bidirectional?: boolean;
  inputUtf8?: boolean;
}

@Component({
  selector: "app-embedded-terminal",
  templateUrl: "./embedded-terminal.component.html",
  styleUrls: ["./embedded-terminal.component.scss"]
})
export class EmbeddedTerminalComponent implements AfterViewInit {
  @ViewChild("term", { static: true }) term: NgTerminal;
  // socket = new WebSocket("0.0.0.0:3000");
  // attachAddon = new AttachAddon(this.socket);

  constructor() {}

  ngOnInit() {}

  ngAfterViewInit() {
    this.term?.write("$ ");

    this.term?.keyEventInput.subscribe(e => {
      console.log("keyboard event:" + e.domEvent.keyCode + ", " + e.key);

      const ev = e.domEvent;
      const printable = !ev.altKey && !ev.ctrlKey && !ev.metaKey;

      if (ev.keyCode === 13) {
        this.term.write("\r\n$ ");
      } else if (ev.keyCode === 8) {
        // Do not delete the prompt
        if (this.term.underlying.buffer.cursorX > 2) {
          this.term.write("\b \b");
        }
      } else if (printable) {
        this.term.write(e.key);
      }
    });
  }

  public onKeyEvent(event: any) {
    console.log(event);
  }
}
