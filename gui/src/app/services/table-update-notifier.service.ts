import { Injectable, EventEmitter } from "@angular/core";
import { Observable, Subject } from "rxjs";

@Injectable({
  providedIn: "root"
})
export class TableUpdateNotifierService {
  public notification: Subject<boolean> = new Subject();

  constructor() {}

  public triggerTableUpdate() {
    this.notification.next(true);
  }

  public getNotification(): Observable<boolean> {
    return this.notification.asObservable();
  }
}
