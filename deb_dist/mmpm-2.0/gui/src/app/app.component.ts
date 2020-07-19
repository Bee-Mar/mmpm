import { Component } from "@angular/core";
import { MatIconRegistry } from "@angular/material/icon";
import { DomSanitizer } from "@angular/platform-browser";
import { environment } from "../environments/environment";
import * as Cookie from "js-cookie";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"],
  providers: []
})
export class AppComponent {
  constructor(private registry: MatIconRegistry, private sanitizer: DomSanitizer) {
    this.registry.addSvgIcon(
      "paypal",
      this.sanitizer.bypassSecurityTrustResourceUrl(`${environment.assetsPath}/icons/paypal.svg`)
    );
  }

  private mmpmThemeCookie = "MMPM-theme";

  public themeColor = Cookie.get("MMPM-theme") ?? "dark-theme";

  public webSSHLocation = `http://${window.location.hostname}:7892`;
  public title = "gui";

  public toggleTheme(): void {

    const body = document.getElementsByTagName("body")[0];
    body.classList.remove(this.themeColor);

    // switch theme
    (this.themeColor == "light-theme") ? this.themeColor = "dark-theme" : this.themeColor = "light-theme";

    body.classList.add(this.themeColor);

    //save it to local storage
    Cookie.set(this.mmpmThemeCookie, this.themeColor);
  }
}
