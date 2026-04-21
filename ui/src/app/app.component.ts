import { Component, AfterViewInit } from "@angular/core";
import { MagicMirrorPackage } from "@/models/magicmirror-package";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"],
  standalone: false,
})
export class AppComponent implements AfterViewInit {
  public activeTab: string = localStorage.getItem("mmpm.tab") || "marketplace";
  public dockTab: string = "cart";
  public viewMode: "cards" | "table" = (localStorage.getItem("mmpm.view") as "cards" | "table") || "cards";
  public mmStatus: string = "unknown";
  public showControllerPopover: boolean = false;
  public loading: boolean = false;

  public selectedPackages: MagicMirrorPackage[] = [];
  public selectedPackage: MagicMirrorPackage | null = null;

  public ngAfterViewInit(): void {
    const splash = document.getElementById('mmpm-splash');
    if (splash) {
      splash.classList.add('splash-out');
      setTimeout(() => splash.remove(), 520);
    }
  }

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

  public setDockPanel(panel: string): void {
    this.dockTab = panel;
  }

  public get dockPanelTitle(): string {
    const titles: Record<string, string> = {
      'add-package': 'Add Custom Package',
      'remove-package': 'Remove Custom Packages',
      'db-info': 'Database Info',
      'db-upgrades': 'Available Upgrades',
    };
    return titles[this.dockTab] ?? '';
  }
}
