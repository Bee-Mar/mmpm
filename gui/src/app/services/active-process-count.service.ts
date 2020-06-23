import { Injectable } from "@angular/core";
import { Subject, Observable } from "rxjs";
import { ActiveProcess } from "src/app/interfaces/interfaces";

@Injectable({
  providedIn: "root"
})
export class ActiveProcessCountService {
  private activeProcesses: Map<number, ActiveProcess> = new Map<number, ActiveProcess>();
  private subject: Subject<Map<number, ActiveProcess>> = new Subject();
  private ticketNumber: number = 0;

  constructor() {}

  public ngOnInit() {}

  public insertProcess(process: ActiveProcess): number {
    this.activeProcesses.set(this.ticketNumber++, process);
    this.subject.next(this.activeProcesses);
    return this.ticketNumber - 1;
  }

  public removeProcess(key: number): boolean {
    const result: boolean = this.activeProcesses.delete(key);
    this.subject.next(this.activeProcesses);
    return result;
  }

  public getProcesses(): Observable<Map<number, ActiveProcess>> {
    return this.subject.asObservable();
  }
}
