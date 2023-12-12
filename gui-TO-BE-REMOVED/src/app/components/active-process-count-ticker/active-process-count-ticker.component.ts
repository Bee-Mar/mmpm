import { Component, OnInit } from "@angular/core";
import { ActiveProcessCountService } from "src/app/services/active-process-count.service";
import { ActiveProcessesModalComponent } from "src/app/components/active-processes-modal/active-processes-modal.component";
import { ActiveProcess } from "src/app/interfaces/interfaces";
import { Subscription } from "rxjs";
import { MatDialog } from "@angular/material/dialog";

@Component({
  selector: "app-active-process-count-ticker",
  templateUrl: "./active-process-count-ticker.component.html",
  styleUrls: ["./active-process-count-ticker.component.scss"],
})
export class ActiveProcessCountTickerComponent implements OnInit {
  constructor(private activeProcessService: ActiveProcessCountService, private dialog: MatDialog) {}

  private subscription: Subscription;
  public activeProcesses: Map<number, ActiveProcess> = new Map<number, ActiveProcess>();

  public ngOnInit(): void {
    this.subscription = this.activeProcessService.getProcesses().subscribe((processes: Map<number, ActiveProcess>) => {
      this.activeProcesses = processes;
    });
  }

  public ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  public showActiveProcesses(): void {
    this.dialog.open(ActiveProcessesModalComponent, {
      width: "45vw",
      height: "50vh",
      disableClose: true,
      data: {
        service: this.activeProcessService,
      },
    });
  }
}
