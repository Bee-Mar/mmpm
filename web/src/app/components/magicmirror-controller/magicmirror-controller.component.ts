import {Component, OnDestroy, OnInit} from '@angular/core';
import {io} from "socket.io-client";
import {MMPMEnv} from '@/models/mmpm-env';
import {MagicMirrorModule} from '@/models/magicmirror-module';
import {SharedStoreService} from '@/services/shared-store.service';
import {Subscription} from 'rxjs';

@Component({
  selector: 'app-magicmirror-controller',
  templateUrl: './magicmirror-controller.component.html',
  styleUrls: ['./magicmirror-controller.component.scss']
})
export class MagicMirrorControllerComponent implements OnInit, OnDestroy {
  constructor(private store: SharedStoreService) {}

  private envSubscription: Subscription = new Subscription();

  public socket: any | null = null;
  public env: MMPMEnv;
  public modules = new Array<MagicMirrorModule>();
  public selectedModules = new Array<MagicMirrorModule>();

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
  }

  public onStop(): void {
    console.log("stop");
  }

  public onRestart(): void {
    console.log("restart");
  }

  public onInstall(): void {
    console.log("install");
  }

  public onRemove(): void {
    console.log("remove");
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




