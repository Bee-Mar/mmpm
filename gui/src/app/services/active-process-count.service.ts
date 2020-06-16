import { Injectable } from "@angular/core";
import { Observable, Subject } from "rxjs";

@Injectable({
  providedIn: "root"
})
export class ActiveProcessCountService {
  public currentCount: Subject<number> = new Subject();

  constructor() {}

  public setCurrentProcessCount(count: number): void {
    this.currentCount.next(count);
  }

  public getCurrentProcessCount(): Observable<number> {
    return this.currentCount.asObservable();
  }
}
