import { Component, OnInit } from "@angular/core";
import { ActiveProcessCountService } from "src/app/services/active-process-count.service";
import { ActiveProcess } from "src/app/interfaces/active-process";
import { Subscription } from "rxjs";

@Component({
  selector: "app-active-process-count-ticker",
  templateUrl: "./active-process-count-ticker.component.html",
  styleUrls: ["./active-process-count-ticker.component.scss"]
})
export class ActiveProcessCountTickerComponent implements OnInit {
  constructor(private activeProcessService: ActiveProcessCountService) { }
  public currentCount: number = 0;
  private subscription: Subscription;

  ngOnInit(): void {
    this.subscription = this.activeProcessService.getProcesses().subscribe((processes: Map<number, ActiveProcess>) => {
      this.currentCount = processes.size;
    });
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

}
