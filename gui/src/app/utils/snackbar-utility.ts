import { MatSnackBar } from "@angular/material/snack-bar";

export class SnackbarUtility {

  private snackbarSettings: object = { duration: 5000 };

  constructor(
    private snackbar: MatSnackBar,
  ) {}

  public notification(message: string): void {
    this.snackbar.open(message, "Close", this.snackbarSettings);
  }

  public snackbarNotificationFailure(message: string): void {
    this.snackbar.open(message, "Close", this.snackbarSettings);
  }

  public snackbarNotificationSuccess(message: string): void {
    this.snackbar.open(message, "Close", this.snackbarSettings);
  }

  public setSnackbarSettings(settings: object): void {
    this.snackbarSettings = settings;
  }

}
