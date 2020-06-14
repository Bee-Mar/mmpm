import { Injectable } from "@angular/core";
import { Observable, Subject } from "rxjs";

@Injectable({
  providedIn: "root"
})
export class ActiveProcessCountService {
  public currentCount: Subject<number> = new Subject();

  constructor() {}

  public updateCurrentProcessCount(count: number): void {
    this.currentCount.next(count);
  }

  public getCurrentCount(): Observable<number> {
    return this.currentCount.asObservable();
  }
}
