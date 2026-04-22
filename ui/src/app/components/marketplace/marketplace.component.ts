import { Component, OnInit, OnDestroy, Input, Output, EventEmitter, inject } from '@angular/core';
import { MagicMirrorPackage } from '@/models/magicmirror-package';
import { SharedStoreService } from '@/services/shared-store.service';
import { Subscription } from 'rxjs';
import { getModuleIcon, ModuleIcon } from '@/utils/module-icon';

@Component({
  selector: 'app-marketplace',
  templateUrl: './marketplace.component.html',
  styleUrls: ['./marketplace.component.scss'],
  standalone: false,
})
export class MarketPlaceComponent implements OnInit, OnDestroy {
  private store = inject(SharedStoreService);
  private packagesSubscription: Subscription = new Subscription();

  @Input() viewMode: 'cards' | 'table' = 'cards';
  @Output() viewModeChange = new EventEmitter<'cards' | 'table'>();
  @Input() selectedPackages: MagicMirrorPackage[] = [];
  @Output() selectedPackagesChange = new EventEmitter<MagicMirrorPackage[]>();
  @Output() selectedPackageChange = new EventEmitter<MagicMirrorPackage | null>();
  @Output() openPanel = new EventEmitter<string>();

  public loading: boolean = true;

  public packages: MagicMirrorPackage[] = [];
  public categories: string[] = [];
  public selectedCategory: string = 'all';
  public searchQuery: string = '';
  public sortField: 'stars' | null = null;
  public sortDir: 'asc' | 'desc' = 'desc';

  public get filteredPackages(): MagicMirrorPackage[] {
    const filtered = this.packages.filter(pkg => {
      const matchesCategory = this.selectedCategory === 'all' || pkg.category === this.selectedCategory;
      if (!matchesCategory) return false;
      if (!this.searchQuery) return true;
      const q = this.searchQuery.toLowerCase();
      return pkg.title.toLowerCase().includes(q)
        || pkg.author.toLowerCase().includes(q)
        || pkg.description.toLowerCase().includes(q);
    });

    if (this.sortField === 'stars') {
      const dir = this.sortDir === 'desc' ? -1 : 1;
      return [...filtered].sort((a, b) => (a.stars - b.stars) * dir);
    }

    return filtered;
  }

  public toggleSort(field: 'stars'): void {
    if (this.sortField === field) {
      this.sortDir = this.sortDir === 'desc' ? 'asc' : 'desc';
    } else {
      this.sortField = field;
      this.sortDir = 'desc';
    }
  }

  public get installedCount(): number {
    return this.packages.filter(p => p.is_installed).length;
  }

  public get upgradableCount(): number {
    return this.packages.filter(p => p.is_upgradable).length;
  }

  public categoryCount(cat: string): number {
    return this.packages.filter(p => p.category === cat).length;
  }

  public isSelected(pkg: MagicMirrorPackage): boolean {
    return this.selectedPackages.some(p => p.title === pkg.title && p.repository === pkg.repository);
  }

  public isInstallable(pkg: MagicMirrorPackage): boolean {
    return pkg.title.toLowerCase() !== 'mmpm';
  }

  public toggleSelect(pkg: MagicMirrorPackage): void {
    if (!pkg.is_installed && !this.isInstallable(pkg)) return;
    const next = this.isSelected(pkg)
      ? this.selectedPackages.filter(p => !(p.title === pkg.title && p.repository === pkg.repository))
      : [...this.selectedPackages, pkg];
    this.selectedPackagesChange.emit(next);
  }

  public openDetails(pkg: MagicMirrorPackage): void {
    this.selectedPackageChange.emit(pkg);
  }

  public getModuleIcon(pkg: MagicMirrorPackage): ModuleIcon {
    return getModuleIcon(pkg);
  }

  public ngOnInit(): void {
    this.packagesSubscription = this.store.packages.subscribe((packages: MagicMirrorPackage[]) => {
      this.packages = packages;

      this.categories = ['all', ...packages
        .map(pkg => pkg.category)
        .filter((cat, idx, self) => cat && self.indexOf(cat) === idx)
        .sort()
      ];

      this.loading = false;
    });
  }

  public ngOnDestroy(): void {
    this.packagesSubscription.unsubscribe();
  }
}
