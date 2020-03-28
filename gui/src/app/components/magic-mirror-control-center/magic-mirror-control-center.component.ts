import { Component, OnInit } from "@angular/core";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { ConfirmationDialogComponent } from "src/app/components/confirmation-dialog/confirmation-dialog.component";

@Component({
  selector: "app-magic-mirror-control-center",
  templateUrl: "./magic-mirror-control-center.component.html",
  styleUrls: ["./magic-mirror-control-center.component.scss"]
})
export class MagicMirrorControlCenterComponent implements OnInit {
  constructor(
    private api: RestApiService,
    private snackbar: MatSnackBar,
    public dialog: MatDialog
  ) {}

  private snackbarSettings: object = { duration: 3000 };

  private working = () => {
    this.snackbar.open(
      "This may take a moment to have an effect ...",
      "Close",
      this.snackbarSettings
    );
  };

  private executing = () => {
    this.snackbar.open("Process executing ...", "Close", this.snackbarSettings);
  };

  ngOnInit(): void {}

  onSendControlSignal(url: string): void {
    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      height: "33vh",
      width: "33vh"
    });

    dialogRef.afterClosed().subscribe((response) => {
      if (response === false) {
        return;
      }
    });

    this.executing();

    this.api.basicGet(url).subscribe((response) => {
      this.working();
    });
  }
}
