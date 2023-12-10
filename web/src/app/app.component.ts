import {Component, OnInit} from "@angular/core";
import {get_cookie, set_cookie} from "./utils/utils";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"],
})
export class AppComponent implements OnInit {
  public title = "MagicMirror Package Manager";
  public active_index = 0;

  public ngOnInit(): void {
    this.active_index = Number(get_cookie("mmpm-active-tab-index", "0"));
  }

  public on_tab_change(index: number) {
    set_cookie("mmpm-active-tab-index", String(index));
  }
}
