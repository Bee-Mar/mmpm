import { Component, OnInit } from "@angular/core";
import { getCookie, setCookie } from "./utils/utils";
import { APIResponse, BaseAPI } from "./services/api/base-api";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"],
})
export class AppComponent implements OnInit {
  constructor(private base_api: BaseAPI) {}

  public title = "MagicMirror Package Manager";
  public index = 0;

  public ngOnInit(): void {
    this.index = Number(getCookie("mmpm-active-tab-index", "0"));
  }

  public onTabChange(index: number) {
    setCookie("mmpm-active-tab-index", String(index));
  }
}
