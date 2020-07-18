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
import { SelectModalComponent } from "src/app/components/select-modal/select-modal.component";
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
  dialogWidth: string;
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
    public mmpmUtility: MMPMUtility,
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
        if (result.fails?.length) {
          this.snackbar.error(`Failed to hide ${result.fails}. Seee MMPM logs for details`)
        }
      });

      this.socket.on("MODULES_HIDDEN", (result: any) => {
        if (result.fails.length) {
          this.snackbar.error(`Failed to hide ${result.fails}. Seee MMPM logs for details`)
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
      dialogWidth: "30vw",
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
      dialogWidth: "30vw",
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
      dialogWidth: "30vw",
    },
    {
      icon: "power_settings_new",
      visibleTooltip: "Reboot RaspberryPi",
      disabledTooltip: "Unable to restart RaspberryPi within a Docker image",
      cols: 1,
      rows: 1,
      badge: null,
      url: URLS.GET.RASPBERRYPI.RESTART,
      message: "Your RaspberryPi will be rebooted.",
      disabled: false,
      dialogWidth: "30vw",
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
      dialogWidth: "33vw",
    },
    {
      icon: "cached",
      visibleTooltip: "Rotate screen",
      disabledTooltip: "Unable to rotate screen within a Docker image",
      cols: 1,
      rows: 1,
      badge: null,
      url: URLS.POST.RASPBERRYPI.ROTATE_SCREEN,
      message: "The screen will be rotated. The RaspberryPi must be restarted to take effect",
      disabled: false,
      dialogWidth: "45vw",
    }
  ];

  private working = () => this.snackbar.notify("This may take a moment ...");
  private executed = () => this.snackbar.notify("Process executed");
  private magicMirrorRunningAlready = () => this.snackbar.error("MagicMirror appears to be running already. If this is a mistake, stop, then start MagicMirror.");

  public sendControlSignal(url: string, message: string, dialogWidth: string): void {

    if (url === URLS.POST.RASPBERRYPI.ROTATE_SCREEN) {
      const selectDialogRef = this.dialog.open(SelectModalComponent, {
        data: {
          title: "Rotate RaspberryPi Screen",
          label: "Degrees",
          choices: [0, 90, 180, 270],
          description: "degrees"
        },
        width: "20vw",
        height: "40vh",
        disableClose: true
      });

      selectDialogRef.afterClosed().subscribe((value) => {

        const confirmationDialogRef = this.dialog.open(ConfirmationDialogComponent, {
          height: "15vh",
          width: dialogWidth,
          data: {
            message
          },
          disableClose: true
        });

        confirmationDialogRef.afterClosed().subscribe((response) => {
          if (!response) {
            return;
          }

          this.api.rotateRaspberryPiScreen(value).then((error: any) => {
            if (error?.error) {
              this.snackbar.error(error.error);
            }
          });

        });
      });
      return;

    } else {
      const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
        height: "15vh",
        width: dialogWidth,
        data: {
          message
        },
        disableClose: true
      });

      dialogRef.afterClosed().subscribe((response) => {
        if (!response) {
          return;
        }

        let ids: Array<number>;

        this.api.retrieve(url).then((success) => {
          if (url === URLS.GET.MAGICMIRROR.START) {
            success ? this.working() : this.magicMirrorRunningAlready();
          } else if (url === URLS.GET.MAGICMIRROR.UPGRADE) {
            success ? this.snackbar.success('Upgraded MagicMirror!') : this.snackbar.error('Failed to upgrade MagicMirror. Please see the MMPM log files for details');
            this.mmpmUtility.deleteProcessIds(ids);
            this.dataStore.retrieveMagicMirrorPackageData();
          } else {
            url === URLS.GET.MAGICMIRROR.RESTART ? this.working() : this.executed();
          }

          this.loadControlCenterData();
        }).catch((error) => { console.log(error); });
      });

    }


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
