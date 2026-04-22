import { Component, AfterViewInit, OnDestroy } from "@angular/core";
import { MagicMirrorPackage } from "@/models/magicmirror-package";

const DOCK_WIDTH_KEY = 'mmpm.dock-width';
const DOCK_MIN = 240;
const DOCK_MAX = 600;
const DOCK_DEFAULT = 340;

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"],
  standalone: false,
})
export class AppComponent implements AfterViewInit, OnDestroy {
  public activeTab: string = localStorage.getItem("mmpm.tab") || "marketplace";
  public dockTab: string = "cart";
  public viewMode: "cards" | "table" = (AppComponent.getCookie("mmpm.view") as "cards" | "table") || "cards";
  public mmStatus: string = "unknown";
  public showControllerPopover: boolean = false;
  public loading: boolean = false;
  public dockWidth: number = Number(localStorage.getItem(DOCK_WIDTH_KEY)) || DOCK_DEFAULT;
  public isResizing = false;
  public isRailExpanded: boolean = localStorage.getItem('mmpm.rail-expanded') === 'true';

  public toggleRail(): void {
    this.isRailExpanded = !this.isRailExpanded;
    localStorage.setItem('mmpm.rail-expanded', String(this.isRailExpanded));
  }

  public selectedPackages: MagicMirrorPackage[] = [];
  public selectedPackage: MagicMirrorPackage | null = null;

  private onMouseMove = (e: MouseEvent): void => {
    const next = Math.min(DOCK_MAX, Math.max(DOCK_MIN, window.innerWidth - e.clientX));
    this.dockWidth = next;
  };

  private onMouseUp = (): void => {
    this.isResizing = false;
    localStorage.setItem(DOCK_WIDTH_KEY, String(this.dockWidth));
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
    window.removeEventListener('mousemove', this.onMouseMove);
    window.removeEventListener('mouseup', this.onMouseUp);
  };

  public onResizeStart(e: MouseEvent): void {
    e.preventDefault();
    this.isResizing = true;
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    window.addEventListener('mousemove', this.onMouseMove);
    window.addEventListener('mouseup', this.onMouseUp);
  }

  public ngOnDestroy(): void {
    window.removeEventListener('mousemove', this.onMouseMove);
    window.removeEventListener('mouseup', this.onMouseUp);
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

}
