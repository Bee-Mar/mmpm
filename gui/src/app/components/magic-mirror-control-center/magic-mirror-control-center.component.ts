import { Component, OnInit } from "@angular/core";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { ConfirmationDialogComponent } from "src/app/components/confirmation-dialog/confirmation-dialog.component";
import { LiveTerminalFeedDialogComponent } from "src/app/components/live-terminal-feed-dialog/live-terminal-feed-dialog.component";
import { DataStoreService } from "src/app/services/data-store.service";
import { TableUpdateNotifierService } from "src/app/services/table-update-notifier.service";
import { URLS } from "src/app/utils/urls";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";
import io from "socket.io-client";

interface Tile {
  icon: string;
  cols: number;
  rows: number;
  tooltip: string;
  message: string;
  url: string;
  disabled: boolean;
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
    public dialog: MatDialog,
    private dataStore: DataStoreService,
    private tableUpdateNotifier: TableUpdateNotifierService,
  ) {}

  public socket: any;
  public outputStream: string = "";
  public magicMirrorIsUpgrable: boolean = false;
  public installedPackages: Array<MagicMirrorPackage>;


  ngOnInit(): void {
    this.socket = io("http://localhost:8080/mmpm", {reconnection: true});
    this.socket.on("connect", () => {
      this.socket.emit("GET_ACTIVE_MODULES");
    });
    this.socket.on("notification", (data: any) => console.log(data));
    this.socket.on("disconnect", (data: any) => console.log(data));
    this.socket.on("MMPM", (data: any) => console.log(data));
    this.socket.on("error", (data: any) => console.log(data));

    this.api.retrieve(URLS.GET.PACKAGES.UPGRADEABLE).then((upgradeable: object) => {
      this.magicMirrorIsUpgrable = upgradeable["MagicMirror"];
    }).catch((error) => console.log(error));

    this.getInstalledPackages();

    this.tableUpdateNotifier.getNotification().subscribe((_) => this.getInstalledPackages(true));
  }

  private getInstalledPackages(refresh: boolean = false): void {
    this.dataStore.getAllInstalledPackages(refresh).then((packages: Array<MagicMirrorPackage>) => {
      this.installedPackages = packages;
    }).catch((error) => console.log(error));
  }

  private liveTerminalFeedDialogSettings: object = {
    width: "75vw",
    height: "75vh"
  };

  public tiles: Tile[] = [
    {
      icon: "live_tv",
      tooltip: "Start MagicMirror",
      cols: 1,
      rows: 1,
      url: URLS.GET.MAGICMIRROR.START,
      message: "MagicMirror will be started.",
      disabled: false,
    },
    {
      icon: "tv_off",
      tooltip: "Stop MagicMirror",
      cols: 1,
      rows: 1,
      url: URLS.GET.MAGICMIRROR.STOP,
      message: "MagicMirror will be stopped.",
      disabled: false,
    },
    {
      icon: "refresh",
      tooltip: "Restart MagicMirror",
      cols: 1,
      rows: 1,
      url: URLS.GET.MAGICMIRROR.RESTART,
      message: "MagicMirror will be restarted.",
      disabled: false,
    },
    {
      icon: "system_update",
      tooltip: this.magicMirrorIsUpgrable ? "Upgrade MagicMirror" : "No MagicMirror upgrades available",
      cols: 1,
      rows: 1,
      url: URLS.GET.MAGICMIRROR.UPGRADE,
      message: "MagicMirror will be upgraded and restarted, if running.",
      disabled: !this.magicMirrorIsUpgrable,
    },
    {
      icon: "power_settings_new",
      tooltip: "Restart RaspberryPi",
      cols: 1,
      rows: 1,
      url: URLS.GET.RASPBERRYPI.RESTART,
      message: "Your RaspberryPi will be rebooted.",
      disabled: false,
    },
    {
      icon: "power_off",
      tooltip: "Shutdown RaspberryPi",
      cols: 1,
      rows: 1,
      url: URLS.GET.RASPBERRYPI.STOP,
      message: "Your RaspberryPi will be powered off.",
      disabled: false,
    },
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


  public sendControlSignal(url: string, message: string): void {

    const data = {
      height: "15vh",
      width: "33vw",
      data: { message }
    };

    const dialogRef = this.dialog.open(ConfirmationDialogComponent, data);

    dialogRef.afterClosed().subscribe((response) => {
      if (!response) return;

      if (url === URLS.GET.MAGICMIRROR.UPGRADE) {
        this.dialog.open(LiveTerminalFeedDialogComponent, this.liveTerminalFeedDialogSettings);
      }

      this.api.retrieve(url).then((success) => {
        if (url === URLS.GET.MAGICMIRROR.START) {
          success ? this.working() : this.magicMirrorRunningAlready();
        } else {
          url === URLS.GET.MAGICMIRROR.RESTART ? this.working() : this.executed();
        }
      }).catch((error) => { console.log(error); });
    });
  }
}
