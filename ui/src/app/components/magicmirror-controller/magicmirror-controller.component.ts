import {Component, HostListener, OnDestroy, OnInit} from "@angular/core";
import {io} from "socket.io-client";
import {MMPMEnv} from "@/models/mmpm-env";
import {MagicMirrorModule} from "@/models/magicmirror-module";
import {MessageService, ConfirmationService, MenuItem} from "primeng/api";
import {APIResponse} from "@/services/api/base-api";
import {MagicMirrorAPI} from "@/services/api/magicmirror-api.service";
import {MagicMirrorControllerAPI} from "@/services/api/magicmirror-controller-api.service";

@Component({
  selector: "app-magicmirror-controller",
  templateUrl: "./magicmirror-controller.component.html",
  styleUrls: ["./magicmirror-controller.component.scss"],
  providers: [MessageService, ConfirmationService],
})
export class MagicMirrorControllerComponent implements OnInit, OnDestroy {
  constructor(private msg: MessageService, private mmControllerApi: MagicMirrorControllerAPI, private mmApi: MagicMirrorAPI, private confirmation: ConfirmationService) {}

  public env: MMPMEnv;
  public openHelpDialog = false;
  public socket: any | null = null;
  public openModuleVisibilityDialog = false;
  public modules = new Array<MagicMirrorModule>();
  public selectedModules = new Array<MagicMirrorModule>();

  // The tooltips don't show up for some reason, which is annoying
  public items: MenuItem[] = [
    {
      icon: "fa-solid fa-eye",
      command: () => {
        this.openModuleVisibilityDialog = true;
      },
      tooltip: "Toggle Modules",
    },
    {
      icon: "fa-solid fa-play",
      command: () => {
        this.onStart();
      },
      tooltip: "Start MagicMirror",
    },
    {
      icon: "fa-solid fa-arrows-rotate",
      command: () => {
        this.onRestart();
      },
      tooltip: "Restart MagicMirror",
    },
    {
      icon: "fa-solid fa-stop",
      command: () => {
        this.onStop();
      },
      tooltip: "Stop MagicMirror",
    },
    {
      icon: "fa-solid fa-download",
      command: () => {
        this.confirmation.confirm({
          message: "Are you sure you want to install MagicMirror?",
          header: "Confirmation",
          icon: "pi pi-exclamation-triangle",
          accept: () => {
            this.onInstall();
          },
          reject: () => {
            return;
          },
        });
      },
      tooltip: "Install MagicMirror",
    },
    {
      icon: "fa-solid fa-trash",
      command: () => {
        this.confirmation.confirm({
          message: "Are you sure you want to remove MagicMirror? This cannot be undone.",
          header: "Confirmation",
          icon: "pi pi-exclamation-triangle",
          accept: () => {
            this.onRemove();
          },
          reject: () => {
            return;
          },
        });
      },
      tooltip: "Remove MagicMirror",
    },
    {
      icon: "fa-solid fa-circle-info",
      command: () => {
        this.openHelpDialog = true;
      },
      tooltip: "Remove MagicMirror",
    },
  ];

  public ngOnInit(): void {
    this.initSocket();
  }

  public ngOnDestroy(): void {
    if (this.socket.connected) {
      this.socket.disconnect();
    }
  }

  public onModuleVisibilityChange(mmModule: MagicMirrorModule) {
    // remember, the value was inverted when it was collected initially
    // to make the toggleButton display as it would be expected
    if (mmModule.hidden) {
      this.mmControllerApi.postShow(mmModule).then((response: APIResponse) => {
        if (response.code !== 200) {
          this.msg.add({severity: "error", summary: "Show Modules", detail: response.message});
        } else {
          this.msg.add({severity: "success", summary: "Show Modules"});
        }
      });
    } else {
      this.mmControllerApi.postHide(mmModule).then((response: APIResponse) => {
        if (response.code !== 200) {
          this.msg.add({severity: "error", summary: "Hid Modules", detail: response.message});
        } else {
          this.msg.add({severity: "success", summary: "Hid Modules"});
        }
      });
    }
  }

  public onStart(): void {
    this.modules = [];

    this.mmControllerApi.getStart().then((response: APIResponse) => {
      if (response.code === 200) {
        setTimeout(() => {
          this.initSocket();
        }, 3000);

        this.msg.add({severity: "success", summary: "Start MagicMirror", detail: "Successfully started MagicMirror"});
      } else {
        this.msg.add({severity: "error", summary: "Start MagicMirror", detail: response.message});
      }
    });
  }

  public onStop(): void {
    this.modules = [];
    this.socket.disconnect();
    this.socket.close();

    this.mmControllerApi.getStop().then((response: APIResponse) => {
      if (response.code === 200) {
        this.msg.add({severity: "success", summary: "Stop MagicMirror", detail: "Successfully stopped MagicMirror"});
      } else {
        this.msg.add({severity: "error", summary: "Stop MagicMirror", detail: response.message});
      }
    });
  }

  public onRestart(): void {
    this.modules = [];
    this.socket.disconnect();
    this.socket.close();

    this.mmControllerApi.getRestart().then((response: APIResponse) => {
      if (response.code === 200) {
        setTimeout(() => {
          this.initSocket();
        }, 3000);

        this.msg.add({severity: "success", summary: "Restart MagicMirror", detail: "Successfully restarted MagicMirror"});
      } else {
        this.msg.add({severity: "error", summary: "Restart MagicMirror", detail: response.message});
      }
    });
  }

  public onInstall(): void {
    this.mmApi.getInstall().then((response: APIResponse) => {
      if (response.code === 200) {
        this.msg.add({severity: "success", summary: "Install MagicMirror", detail: "Successfully installed MagicMirror"});
      } else {
        this.msg.add({severity: "error", summary: "Install MagicMirror", detail: response.message});
      }
    });
  }

  public onRemove(): void {
    this.mmApi.getRemove().then((response: APIResponse) => {
      if (response.code === 200) {
        this.msg.add({severity: "success", summary: "Remove MagicMirror", detail: "Successfully removed MagicMirror"});
      } else {
        this.msg.add({severity: "error", summary: "Remove MagicMirror", detail: response.message});
      }
    });
  }

  public initSocket(): void {
    console.log("Initializing socket");

    this.socket = io(`${window.location.hostname}:8907`, {reconnection: true});

    this.socket.on("connect", () => {
      console.log("Connected to MMPM Socket.IO Repeater");
      this.socket.emit("request_modules");
    });

    this.socket.on("reconnect", () => {
      console.log("Reconnected to MMPM Socket.IO Repeater");
      this.socket.emit("request_modules");
    });

    this.socket.on("disconnect", (error) => {
      this.modules = [];
      console.log(error);
    });

    this.socket.on("error", (error) => {
      this.modules = [];
      console.log(error);
    });

    this.socket.on("modules", (modules: Array<MagicMirrorModule>) => {
      console.log("Received modules from MMPM Socket.IO Repeater");
      this.modules = this.formatModules(modules);
    });

    this.socket.connect();
  }

  private formatModules(modules: Array<MagicMirrorModule>) {
    // only doing this because the property is called "hidden" in the MagicMirror source code
    // and for the toggle button to display it in a sane way, it needs to be inverted
    // otherwise all the toggleButtons will look like they're off, when in reality those modules
    // are visible. It's a little weird, yes.

    for (const mod of modules) {
      mod.hidden = !mod.hidden;
    }

    return modules;
  }

  @HostListener("window:beforeunload", ["$event"])
  public beforeUnload() {
    this.socket.disconnect();
    this.socket.close();
  }
}
