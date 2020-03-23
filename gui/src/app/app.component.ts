import { Component } from "@angular/core";
import { LiveTerminalFeedService } from "src/app/services/live-terminal-feed.service";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"],
  providers: [LiveTerminalFeedService]
})
export class AppComponent {
  title = "gui";
}
