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
  @Input() selectedPackages: MagicMirrorPackage[] = [];
  @Output() selectedPackagesChange = new EventEmitter<MagicMirrorPackage[]>();

  public loading: boolean = true;

  @Output() selectedPackageChange = new EventEmitter<MagicMirrorPackage | null>();

  public packages: MagicMirrorPackage[] = [];
  public categories: string[] = [];
  public selectedCategory: string = 'all';
  public searchQuery: string = '';

  public get filteredPackages(): MagicMirrorPackage[] {
    return this.packages.filter(pkg => {
      const matchesCategory = this.selectedCategory === 'all' || pkg.category === this.selectedCategory;
      if (!matchesCategory) return false;
      if (!this.searchQuery) return true;
      const q = this.searchQuery.toLowerCase();
      return pkg.title.toLowerCase().includes(q)
        || pkg.author.toLowerCase().includes(q)
        || pkg.description.toLowerCase().includes(q);
    });
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

  public toggleSelect(pkg: MagicMirrorPackage): void {
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
