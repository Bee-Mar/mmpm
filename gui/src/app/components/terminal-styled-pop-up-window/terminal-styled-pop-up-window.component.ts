import { Component, OnInit, Inject } from "@angular/core";
import { MatDialogRef, MAT_DIALOG_DATA } from "@angular/material/dialog";

@Component({
  selector: "app-terminal-styled-pop-up-window",
  templateUrl: "./terminal-styled-pop-up-window.component.html",
  styleUrls: ["./terminal-styled-pop-up-window.component.scss"]
})
export class TerminalStyledPopUpWindowComponent implements OnInit {
  constructor(
    private dialogRef: MatDialogRef<TerminalStyledPopUpWindowComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  ngOnInit(): void {}

  onNoClick() {
    this.dialogRef.close();
  }
}
