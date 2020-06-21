import { Injectable } from "@angular/core";
import { Subject, Observable } from "rxjs";
import { ActiveProcess } from "src/app/interfaces/active-process";

@Injectable({
  providedIn: "root"
})
export class ActiveProcessCountService {
  private activeProcesses: Map<number, ActiveProcess> = new Map<number, ActiveProcess>();
  private ticketNumber: number = 0;
  private subject: Subject<Map<number, ActiveProcess>> = new Subject();

  constructor() {}

  public ngOnInit() {}

  public insertProcess(process: ActiveProcess): number {
    this.activeProcesses.set(this.ticketNumber++, process);
    this.subject.next(this.activeProcesses);
    return this.ticketNumber - 1;
  }

  public removeProcess(key: number) {
    this.activeProcesses.delete(key);
    console.log(this.activeProcesses);
    this.subject.next(this.activeProcesses);
  }

  public getProcesses(): Observable<Map<number, ActiveProcess>> {
    return this.subject.asObservable();
  }
}
