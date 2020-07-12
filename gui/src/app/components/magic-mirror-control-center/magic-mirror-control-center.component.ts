import { Component, OnInit } from "@angular/core";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { ConfirmationDialogComponent } from "src/app/components/confirmation-dialog/confirmation-dialog.component";
import { LiveTerminalFeedDialogComponent } from "src/app/components/live-terminal-feed-dialog/live-terminal-feed-dialog.component";
import { DataStoreService } from "src/app/services/data-store.service";
import { URLS } from "src/app/utils/urls";
import { ActiveModule } from "src/app/interfaces/interfaces";
import { MatSlideToggleChange } from "@angular/material/slide-toggle";
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
    private dataStore: DataStoreService,
    public dialog: MatDialog,
  ) {}

  private mmpmEnvVars: Map<string, object>;

  public socket: any;
  public outputStream: string = "";
  public magicMirrorIsUpgrable: boolean = false;
  public activeModules: Array<ActiveModule>;
  public magicMirrorStream: string = "";
  public magicmirrorUri: string = "";

  ngOnInit(): void {
    this.activeModules = new Array<ActiveModule>();

    this.dataStore.mmpmEnvironmentVariables.subscribe((envVars: Map<string, object>) => {
      this.mmpmEnvVars = new Map<string, object>();
      this.mmpmEnvVars = envVars;
      this.initWebSocket(this.mmpmEnvVars?.get("MMPM_MAGICMIRROR_URI")["value"]);
    });
  }

  public ngOnDestroy(): void {
    this.socket.disconnect();
  }

  public initWebSocket(uri: string): void {
    this.socket = io(`${uri}/mmpm`, {reconnection: true});
    this.socket.on("connect", () => this.socket.emit("FROM_MMPM_APP_get_active_modules"));
    this.socket.on("notification", (data: any) => console.log(data));
    this.socket.on("disconnect", (data: any) => console.log(data));

    this.socket.on("MODULES_VISIBLE", (result: any) => {
      console.log(result);
    });

    this.socket.on("MODULES_HIDDEN", (result: any) => {
      if (result.fails.length) {
        console.log(result);
      }
    });

    this.socket.on("ACTIVE_MODULES", (active: any) => {
      if (active) {
        console.log(active);
        this.activeModules = new Array<ActiveModule>();
        for (const activeModule of active) {
          this.activeModules.push({
            name: activeModule["name"],
            visible: !activeModule["hidden"]
          });
        }
      }
    });

    this.socket.on("MAGICMIRROR_LOGS", (data: any) => {
      this.magicMirrorStream += data.notification + "\n";
      console.log(data)
    });

    this.socket.on("error", (data: any) => console.log(data));

    this.api.retrieve(URLS.GET.PACKAGES.UPGRADEABLE).then((upgradeable: object) => {
      this.magicMirrorIsUpgrable = upgradeable["MagicMirror"];
    }).catch((error) => console.log(error));

  }

  public toggle(event: MatSlideToggleChange, active: ActiveModule) {
    if (event.checked) {
      this.socket.emit("FROM_MMPM_APP_show_modules", [active.name]);
    } else {
      this.socket.emit("FROM_MMPM_APP_hide_modules", [active.name]);
    }
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

  public downloadLogs(): void {
    this.api.getLogFiles().then((file) => {

      const blob = new Blob([file], {type: 'application/zip'});
      const date = new Date();

      const fileName: string = `mmpm-logs-${date.getFullYear()}-${date.getMonth()}-${date.getDay()}.zip`;
      const url: string = URL.createObjectURL(blob);
      const a: HTMLAnchorElement = document.createElement('a') as HTMLAnchorElement;

      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();

      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }).catch((error) => console.log(error));
  }
}
