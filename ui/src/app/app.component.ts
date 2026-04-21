import { Component } from "@angular/core";
import { MagicMirrorPackage } from "@/models/magicmirror-package";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"],
  standalone: false,
})
export class AppComponent {
  public activeTab: string = localStorage.getItem("mmpm.tab") || "marketplace";
  public dockTab: string = "cart";
  public viewMode: "cards" | "table" = (localStorage.getItem("mmpm.view") as "cards" | "table") || "cards";
  public mmStatus: string = "unknown";
  public showControllerPopover: boolean = false;
  public loading: boolean = false;

  public selectedPackages: MagicMirrorPackage[] = [];
  public selectedPackage: MagicMirrorPackage | null = null;

  public setTab(tab: string): void {
    this.activeTab = tab;
    localStorage.setItem("mmpm.tab", tab);
  }

  public setViewMode(mode: "cards" | "table"): void {
    this.viewMode = mode;
    localStorage.setItem("mmpm.view", mode);
  }

  public onPackageSelected(pkg: MagicMirrorPackage | null): void {
    this.selectedPackage = pkg;
    if (pkg) {
      this.dockTab = "details";
    }
  }

  public onToggleCart(): void {
    this.dockTab = this.dockTab === "cart" ? "details" : "cart";
  }
}
