import { Component, AfterViewInit, OnInit } from "@angular/core";
import { MagicMirrorPackage } from "@/models/magicmirror-package";

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"],
  standalone: false,
})
export class AppComponent implements OnInit, AfterViewInit {
  public activeTab: string = localStorage.getItem("mmpm.tab") || "marketplace";
  public dockTab: string = "cart";
  public viewMode: "cards" | "table" = (AppComponent.getCookie("mmpm.view") as "cards" | "table") || "cards";
  public mmStatus: string = "unknown";
  public showControllerPopover: boolean = false;
  public loading: boolean = false;
  public theme: "dark" | "light" = (localStorage.getItem("mmpm.theme") as "dark" | "light") || "dark";

  public selectedPackages: MagicMirrorPackage[] = [];
  public selectedPackage: MagicMirrorPackage | null = null;

  public ngOnInit(): void {
    this.applyTheme();
  }

  public ngAfterViewInit(): void {
    const splash = document.getElementById('mmpm-splash');
    if (!splash) return;
    const elapsed = Date.now() - ((window as unknown as Record<string, number>)['__splashStart'] ?? 0);
    const remaining = Math.max(0, 3000 - elapsed);
    setTimeout(() => {
      splash.classList.add('splash-out');
      setTimeout(() => splash.remove(), 520);
    }, remaining);
  }

  public setTab(tab: string): void {
    this.activeTab = tab;
    localStorage.setItem("mmpm.tab", tab);
  }

  public setViewMode(mode: "cards" | "table"): void {
    this.viewMode = mode;
    document.cookie = `mmpm.view=${mode}; path=/; max-age=31536000; SameSite=Lax`;
  }

  private static getCookie(name: string): string {
    const match = document.cookie.split('; ').find(row => row.startsWith(name + '='));
    return match ? match.split('=')[1] : '';
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

  public toggleTheme(): void {
    this.theme = this.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('mmpm.theme', this.theme);
    this.applyTheme();
  }

  private applyTheme(): void {
    document.documentElement.setAttribute('data-theme', this.theme);
  }
}
