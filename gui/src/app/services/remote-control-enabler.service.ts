import { Injectable } from "@angular/core";
import { Observable, Subject } from "rxjs";

@Injectable({
  providedIn: "root"
})
export class RemoteControlEnablerService {
  public notification: Subject<boolean> = new Subject();

  constructor() {}

  public sendNotification(isInstalled: boolean = false): void {
    this.notification.next(isInstalled);
  }

  public getNotification(): Observable<boolean> {
    return this.notification.asObservable();
  }
}
