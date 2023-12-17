import { Component } from "@angular/core";
import { getCookie, setCookie } from "./utils/utils";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"],
})
export class AppComponent {
  public title = "MagicMirror Package Manager";
  public index = Number(getCookie("mmpm-active-tab-index", "0"));

  public onTabChange(index: number) {
    setCookie("mmpm-active-tab-index", String(index));
  }
}
