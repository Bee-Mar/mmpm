import {Component, OnDestroy, OnInit} from '@angular/core';
import {io} from "socket.io-client";
import {MMPMEnv} from '@/models/mmpm-env';
import {MagicMirrorModule} from '@/models/magicmirror-module';
import {SharedStoreService} from '@/services/shared-store.service';
import {Subscription} from 'rxjs';
import {MessageService, ConfirmationService, MenuItem} from 'primeng/api';
import {APIResponse, BaseAPI} from '@/services/api/base-api';

@Component({
  selector: 'app-magicmirror-controller',
  templateUrl: './magicmirror-controller.component.html',
  styleUrls: ['./magicmirror-controller.component.scss'],
  providers: [MessageService, ConfirmationService],
})
export class MagicMirrorControllerComponent implements OnInit, OnDestroy {
  constructor(private store: SharedStoreService, private msg: MessageService, private base_api: BaseAPI, private confirmation: ConfirmationService) {}

  private envSubscription: Subscription = new Subscription();

  public socket: any | null = null;
  public env: MMPMEnv;
  public modules = new Array<MagicMirrorModule>();
  public selectedModules = new Array<MagicMirrorModule>();

  // The tooltips don't show up for some reason, which is annoying
  public items: MenuItem[] = [
    {
      icon: 'fa-solid fa-eye',
      command: () => {
        this.msg.add({severity: 'info', summary: 'Add', detail: 'Data Added'});
      },
      tooltip: "Toggle Modules"
    },
    {
      icon: 'fa-solid fa-play',
      command: () => {
        this.onStart();
      },
      tooltip: "Start MagicMirror"
    },
    {
      icon: 'fa-solid fa-arrows-rotate',
      command: () => {
        this.onRestart();
      },
      tooltip: "Restart MagicMirror"
    },
    {
      icon: 'fa-solid fa-stop',
      command: () => {
        this.onStop();
      },
      tooltip: "Stop MagicMirror"
    },
    {
      icon: 'fa-solid fa-download',
      command: () => {
        this.confirmation.confirm({
          message: 'Are you sure you want to install MagicMirror?',
          header: 'Confirmation',
          icon: 'pi pi-exclamation-triangle',
          accept: () => {
            this.onInstall();
          },
          reject: () => {
            return;
          }
        });
      },
      tooltip: "Install MagicMirror"
    },
    {
      icon: 'fa-solid fa-trash',
      command: () => {

        this.confirmation.confirm({
          message: 'Are you sure you want to remove MagicMirror? This cannot be undone.',
          header: 'Confirmation',
          icon: 'pi pi-exclamation-triangle',
          accept: () => {
            this.onRemove();
          },
          reject: () => {
            return;
          }
        });
      },
      tooltip: "Remove MagicMirror"
    }
  ];


  public ngOnInit(): void {
    this.envSubscription = this.store.env.subscribe((env: MMPMEnv) => {
      this.env = env;

      // only initialize the socket one time after we have the env data
      if ((this.env !== null && this.env !== undefined) && (!this.socket || !this.socket.connected)) {
        this.initSocket();
      }
    });
  }

  public ngOnDestroy(): void {
    if (this.socket.connected) {
      this.socket.disconnect();
    }

    this.envSubscription.unsubscribe();
  }

  public onHide(): void {
    console.log("hide");
  }

  public onShow(): void {
    console.log("show");
  }

  public onStart(): void {
    console.log("start");

    this.base_api.get_("mm-ctl/start").then((response: APIResponse) => {
      if (response.code === 200) {
        this.msg.add({severity: 'success', summary: 'Start MagicMirror', detail: 'Successfully started MagicMirror'});
      } else {
        this.msg.add({severity: 'error', summary: 'Start MagicMirror', detail: response.message});
      }
    });
  }

  public onStop(): void {
    console.log("stop");

    this.base_api.get_("mm-ctl/stop").then((response: APIResponse) => {
      if (response.code === 200) {
        this.msg.add({severity: 'success', summary: 'Stop MagicMirror', detail: 'Successfully stopped MagicMirror'});
      } else {
        this.msg.add({severity: 'error', summary: 'Stop MagicMirror', detail: response.message});
      }
    });
  }

  public onRestart(): void {
    this.base_api.get_("mm-ctl/restart").then((response: APIResponse) => {
      if (response.code === 200) {
        this.msg.add({severity: 'success', summary: 'Restart MagicMirror', detail: 'Successfully restarted MagicMirror'});
      } else {
        this.msg.add({severity: 'error', summary: 'Restart MagicMirror', detail: response.message});
      }
    });
  }

  public onInstall(): void {
    this.base_api.get_("mm-ctl/install").then((response: APIResponse) => {
      if (response.code === 200) {
        this.msg.add({severity: 'success', summary: 'Install MagicMirror', detail: 'Successfully installed MagicMirror'});
      } else {
        this.msg.add({severity: 'error', summary: 'Install MagicMirror', detail: response.message});
      }
    });
  }

  public onRemove(): void {
    this.base_api.get_("mm-ctl/remove").then((response: APIResponse) => {
      if (response.code === 200) {
        this.msg.add({severity: 'success', summary: 'Remove MagicMirror', detail: 'Successfully removed MagicMirror'});
      } else {
        this.msg.add({severity: 'error', summary: 'Remove MagicMirror', detail: response.message});
      }
    });
  }

  public initSocket(): void {
    this.socket = io(`${this.env.MMPM_MAGICMIRROR_URI}/MMM-mmpm`, {reconnection: true});

    this.socket.on("connect", () => {
      console.log("Connected to MagicMirror Socket.IO server");
      this.socket.emit("FROM_MMPM_APP_get_active_modules");
    });

    this.socket.on("notification", (data: any) => {
      console.log(data);
    });

    this.socket.on("disconnect", (data: any) => {
      console.log(data);
    });

    // these keywords are used in node_helper.js and mmpm.js within the mmpm magicmirror module
    this.socket.on("MODULES_TOGGLED", (result: any) => {
      if (result.fails?.length) {
        console.log(`Failed to hide ${result.fails}. See MMPM logs for details`);
      }
    });

    this.socket.on("ACTIVE_MODULES", (modules: Array<MagicMirrorModule>) => {
      if (modules?.length) {
        this.modules = modules;
        console.log(this.modules);
      } else {
        console.log("No active modules returned from the MMM-mmpm module");
      }
    });

    this.socket.on("error", (data: any) => {
      console.log(data);
    });

  }
}




