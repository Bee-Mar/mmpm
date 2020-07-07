import { Component, OnInit, ViewEncapsulation } from "@angular/core";
import { MatSnackBar, MatSnackBarConfig } from "@angular/material/snack-bar";

@Component({
  selector: "app-custom-snackbar",
  templateUrl: "./custom-snackbar.component.html",
  styleUrls: ["./custom-snackbar.component.scss"],
  encapsulation: ViewEncapsulation.None
})
export class CustomSnackbarComponent implements OnInit {
  constructor(private snackbar: MatSnackBar) { }

  private CLOSE: string = "Close";
  private config: MatSnackBarConfig = {duration: 3000};

  ngOnInit(): void {}

  public notify(message: string): void {
    this.config.panelClass = "notify";
    this.snackbar.open(message, this.CLOSE, this.config);
  }

  public success(message: string): void {
    this.config.panelClass = "success";
    this.snackbar.open(message, this.CLOSE, this.config);
  }

  public error(message: string): void {
    this.config.panelClass = "error";
    this.snackbar.open(message, this.CLOSE, this.config);
  }
}
