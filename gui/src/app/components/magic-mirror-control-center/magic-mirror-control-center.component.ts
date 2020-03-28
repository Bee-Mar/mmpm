import { Component, OnInit } from "@angular/core";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { ConfirmationDialogComponent } from "src/app/components/confirmation-dialog/confirmation-dialog.component";

interface Tile {
  icon: string;
  cols: number;
  rows: number;
  tooltip: string;
  url: string;
}

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

  tiles: Tile[] = [
    {
      icon: "refresh",
      tooltip: "Restart MagicMirror",
      cols: 1,
      rows: 1,
      url: "/restart-magicmirror"
    },
    {
      icon: "live_tv",
      tooltip: "Start MagicMirror",
      cols: 1,
      rows: 1,
      url: "/start-magicmirror"
    },
    {
      icon: "tv_off",
      tooltip: "Stop MagicMirror",
      cols: 1,
      rows: 1,
      url: "/stop-magicmirror"
    },
    {
      icon: "power_settings_new",
      tooltip: "Restart RaspberryPi",
      cols: 1,
      rows: 1,
      url: "/restart-raspberrypi"
    },
    {
      icon: "power_off",
      tooltip: "Shutdown RaspberryPi",
      cols: 2,
      rows: 1,
      url: "/shutdown-raspberrypi"
    }
  ];
  private snackbarSettings: object = { duration: 5000 };

  private working = () => {
    this.snackbar.open(
      "This may take a moment ...",
      "Close",
      this.snackbarSettings
    );
  };

  private executed = () => {
    this.snackbar.open("Process executed", "Close", this.snackbarSettings);
  };

  private executing = () => {
    this.snackbar.open("Process executing ...", "Close", this.snackbarSettings);
  };

  private magicMirrorRunningAlready = () => {
    this.snackbar.open(
      "MagicMirror appears to be running already. If this is a mistake, stop, then start MagicMirror.",
      "Close",
      this.snackbarSettings
    );
  };

  ngOnInit(): void {}

  sendControlSignal(url: string): void {
    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      height: "15vh",
      width: "15vw"
    });

    dialogRef.afterClosed().subscribe((response) => {
      if (!response) return;

      this.executing();

      this.api.retrieve(url).subscribe((success) => {
        if (url === "/start-magicmirror") {
          success ? this.working() : this.magicMirrorRunningAlready();
        } else {
          url === "/restart-magicmirror" ? this.working() : this.executed();
        }
      });
    });
  }
}
