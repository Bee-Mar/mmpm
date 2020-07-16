import { Component, OnInit } from "@angular/core";
import { RestApiService } from "src/app/services/rest-api.service";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { ConfirmationDialogComponent } from "src/app/components/confirmation-dialog/confirmation-dialog.component";
import { CustomSnackbarComponent } from "src/app/components/custom-snackbar/custom-snackbar.component";
import { DataStoreService } from "src/app/services/data-store.service";
import { URLS } from "src/app/utils/urls";
import { ActiveModule } from "src/app/interfaces/interfaces";
import { MatSlideToggleChange } from "@angular/material/slide-toggle";
import { MMPMUtility } from "src/app/utils/mmpm-utility";
import { MagicMirrorPackage } from "src/app/interfaces/interfaces";
import io from "socket.io-client";

interface Tile {
  icon: string;
  cols: number;
  rows: number;
  visibleTooltip: string;
  disabledTooltip: string;
  message: string;
  badge: number;
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
    private _snackbar: MatSnackBar,
    private dataStore: DataStoreService,
    private mmpmUtility: MMPMUtility,
    public dialog: MatDialog,
  ) {}

  public socket: any;
  public activeModules: Array<ActiveModule>;
  public mmpmEnvVars: Map<string, string>;
  private snackbar: CustomSnackbarComponent = new CustomSnackbarComponent(this._snackbar);

  public ngOnInit(): void {
    this.loadControlCenterData();
  }

  public loadControlCenterData(): void {
    this.activeModules = new Array<ActiveModule>();

    this.api.retrieve(URLS.GET.MMPM.ENVIRONMENT_VARS).then((envVars: any) => {
      this.mmpmEnvVars = new Map<string, string>();

      Object.keys(envVars).forEach((key) => this.mmpmEnvVars.set(key, envVars[key]));

      const mmpmIsDockerImage: boolean = Boolean(this.mmpmEnvVars?.get("MMPM_IS_DOCKER_IMAGE"));
      this.tiles.forEach((t) => t.disabled = mmpmIsDockerImage);

      this.socket = io(`${this.mmpmEnvVars?.get("MMPM_MAGICMIRROR_URI")}/mmpm`, {reconnection: true});
      this.socket.on("connect", () => this.socket.emit("FROM_MMPM_APP_get_active_modules"));
      this.socket.on("notification", (data: any) => console.log(data));
      this.socket.on("disconnect", (data: any) => console.log(data));

      this.socket.on("MODULES_SHOWN", (result: any) => {
        console.log(result);
      });

      this.socket.on("MODULES_HIDDEN", (result: any) => {
        if (result.fails.length) {
          console.log(result);
        }
      });

      this.socket.on("ACTIVE_MODULES", (active: any) => {
        if (active) {
          this.activeModules = new Array<ActiveModule>();
          for (const activeModule of active) {
            this.activeModules.push({
              name: activeModule["name"],
              visible: !activeModule["hidden"]
            });
          }
        }
      });

      this.socket.on("error", (data: any) => console.log(data));

      this.dataStore.upgradeablePackages.subscribe((upgradeable: any) => {
        this.tiles.forEach((t) => {
          if (t.url === URLS.GET.MAGICMIRROR.UPGRADE) {
            t.disabled = !upgradeable.MagicMirror;
            t.badge = t.disabled ? null : 1;

            if (!mmpmIsDockerImage) {
              t.disabledTooltip = "No upgrades available for MagicMirror"
            }
          }
        });
      });

    }).catch((error) => console.log(error));
  }

  public ngOnDestroy(): void {
    this.socket.disconnect();
  }

  public toggle(event: MatSlideToggleChange, active: ActiveModule) {
    if (event.checked) {
      this.socket.emit("FROM_MMPM_APP_show_modules", [active.name]);
    } else {
      this.socket.emit("FROM_MMPM_APP_hide_modules", [active.name]);
    }
  }

  public tiles: Tile[] = [
    {
      icon: "live_tv",
      visibleTooltip: "Start MagicMirror",
      disabledTooltip: "Unable to start MagicMirror within a Docker image",
      cols: 1,
      rows: 1,
      badge: null,
      url: URLS.GET.MAGICMIRROR.START,
      message: "MagicMirror will be started.",
      disabled: false,
    },
    {
      icon: "tv_off",
      visibleTooltip: "Stop MagicMirror",
      disabledTooltip: "Unable to stop MagicMirror within a Docker image",
      cols: 1,
      rows: 1,
      badge: null,
      url: URLS.GET.MAGICMIRROR.STOP,
      message: "MagicMirror will be stopped.",
      disabled: false,
    },
    {
      icon: "refresh",
      visibleTooltip: "Restart MagicMirror",
      disabledTooltip: "Unable to restart MagicMirror within a Docker image",
      cols: 1,
      rows: 1,
      badge: null,
      url: URLS.GET.MAGICMIRROR.RESTART,
      message: "MagicMirror will be restarted.",
      disabled: false,
    },
    {
      icon: "system_update",
      visibleTooltip: "Upgrade MagicMirror",
      disabledTooltip: "Unable to upgrade MagicMirror within a Docker image",
      cols: 1,
      rows: 1,
      badge: null,
      url: URLS.GET.MAGICMIRROR.UPGRADE,
      message: "MagicMirror will be upgraded and restarted, if running.",
      disabled: false,
    },
    {
      icon: "power_settings_new",
      visibleTooltip: "Restart RaspberryPi",
      disabledTooltip: "Unable to restart RaspberryPi within a Docker image",
      cols: 1,
      rows: 1,
      badge: null,
      url: URLS.GET.RASPBERRYPI.RESTART,
      message: "Your RaspberryPi will be rebooted.",
      disabled: false,
    },
    {
      icon: "power_off",
      visibleTooltip: "Shutdown RaspberryPi",
      disabledTooltip: "Unable to shutdown RaspberryPi within a Docker image",
      cols: 1,
      rows: 1,
      badge: null,
      url: URLS.GET.RASPBERRYPI.STOP,
      message: "Your RaspberryPi will be powered off.",
      disabled: false,
    },
  ];

  private working = () => this.snackbar.notify("This may take a moment ...");
  private executed = () => this.snackbar.notify("Process executed");
  private magicMirrorRunningAlready = () => this.snackbar.error("MagicMirror appears to be running already. If this is a mistake, stop, then start MagicMirror.");

  public sendControlSignal(url: string, message: string): void {
    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      height: "15vh",
      width: "33vw",
      data: {
        message
      }
    });

    dialogRef.afterClosed().subscribe((response) => {
      if (!response) {
        return;
      }

      let ids: Array<number>;

      if (url === URLS.GET.MAGICMIRROR.UPGRADE) {
        // just a dummy MagicMirrorPackage to represent MagicMirror
        const pkg: MagicMirrorPackage = {
          title: "MagicMirror",
          repository: "",
          author: "",
          description: "",
          directory: "",
          category: ""
        };

        this.snackbar.notify('Upgrading MagicMirror. This may take a few moments')
        ids = this.mmpmUtility.saveProcessIds([pkg], "Upgrading");
      }

      this.api.retrieve(url).then((success) => {
        if (url === URLS.GET.MAGICMIRROR.START) {
          success ? this.working() : this.magicMirrorRunningAlready();
        } else if (url === URLS.GET.MAGICMIRROR.UPGRADE) {
          success ? this.snackbar.success('Upgraded MagicMirror!') : this.snackbar.error('Failed to upgrade MagicMirror. Please see the MMPM log files for details');
          this.mmpmUtility.deleteProcessIds(ids);
          this.dataStore.loadData();
        } else {
          url === URLS.GET.MAGICMIRROR.RESTART ? this.working() : this.executed();
        }

        this.loadControlCenterData();
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

  public openUrl(url: string) {
    window.open(url, '_blank');
  }
}
