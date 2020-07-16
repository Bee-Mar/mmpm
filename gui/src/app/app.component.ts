import { Component } from "@angular/core";
import { MatIconRegistry } from "@angular/material/icon";
import { DomSanitizer } from "@angular/platform-browser";
import { environment } from "../environments/environment";

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

  public webSSHLocation = `http://${window.location.hostname}:7892`;
  public title = "gui";

  public toggleTheme(): void {
  }
}
