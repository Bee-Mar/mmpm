import { Component, OnInit, ViewChild, AfterViewInit } from "@angular/core";
import { NgTerminal } from "ng-terminal";

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
  @ViewChild("term", { static: true }) child: NgTerminal;

  constructor() {}

  ngOnInit() {}

  ngAfterViewInit() {
    this.child?.keyEventInput.subscribe(e => {
      console.log("keyboard event:" + e.domEvent.keyCode + ", " + e.key);

      const ev = e.domEvent;
      const printable = !ev.altKey && !ev.ctrlKey && !ev.metaKey;

      if (ev.keyCode === 13) {
        this.child.write("\r\n$ ");
      } else if (ev.keyCode === 8) {
        // Do not delete the prompt
        if (this.child.underlying.buffer.cursorX > 2) {
          this.child.write("\b \b");
        }
      } else if (printable) {
        this.child.write(e.key);
      }
    });
  }

  public onKeyEvent(event: any) {
    console.log(event);
  }
}
