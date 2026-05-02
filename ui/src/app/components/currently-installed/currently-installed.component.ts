import { Component, OnInit, OnDestroy, Input, Output, EventEmitter, inject } from '@angular/core';
import { MagicMirrorPackage } from '@/models/magicmirror-package';
import { SharedStoreService } from '@/services/shared-store.service';
import { Subscription } from 'rxjs';
import { getModuleIcon, ModuleIcon } from '@/utils/module-icon';

@Component({
  selector: 'app-currently-installed',
  templateUrl: './currently-installed.component.html',
  styleUrls: ['./currently-installed.component.scss'],
  standalone: false,
})
export class CurrentlyInstalledComponent implements OnInit, OnDestroy {
  private store = inject(SharedStoreService);
  private sub: Subscription = new Subscription();

  @Input() viewMode: 'cards' | 'table' = 'cards';
  @Output() viewModeChange = new EventEmitter<'cards' | 'table'>();
  @Input() selectedPackages: MagicMirrorPackage[] = [];
  @Output() selectedPackagesChange = new EventEmitter<MagicMirrorPackage[]>();
  @Output() selectedPackageChange = new EventEmitter<MagicMirrorPackage | null>();
  @Output() openPanel = new EventEmitter<string>();

  public loading = true;
  public allInstalled: MagicMirrorPackage[] = [];
  public searchQuery = '';
  public selectedCategory = 'all';
  public categories: string[] = [];
  public sortField: 'title' | 'category' | 'author' | 'stars' | null = null;
  public sortDir: 'asc' | 'desc' = 'asc';

  public colWidths: Record<string, number> = { title: 260, category: 160, author: 120, status: 100, stars: 90 };
  private resizingCol: string | null = null;
  private resizeStartX = 0;
  private resizeStartWidth = 0;

  private onColMouseMove = (e: MouseEvent): void => {
    if (!this.resizingCol) return;
    this.colWidths = { ...this.colWidths, [this.resizingCol]: Math.max(60, this.resizeStartWidth + e.clientX - this.resizeStartX) };
  };

  private onColMouseUp = (): void => {
    this.resizingCol = null;
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
    window.removeEventListener('mousemove', this.onColMouseMove);
    window.removeEventListener('mouseup', this.onColMouseUp);
  };

  public startColResize(e: MouseEvent, col: string): void {
    e.preventDefault();
    e.stopPropagation();
    this.resizingCol = col;
    this.resizeStartX = e.clientX;
    this.resizeStartWidth = this.colWidths[col];
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    window.addEventListener('mousemove', this.onColMouseMove);
    window.addEventListener('mouseup', this.onColMouseUp);
  }

  public get filteredPackages(): MagicMirrorPackage[] {
    const filtered = this.allInstalled.filter(pkg => {
      const matchesCategory = this.selectedCategory === 'all' || pkg.category === this.selectedCategory;
      if (!matchesCategory) return false;
      if (!this.searchQuery) return true;
      const q = this.searchQuery.toLowerCase();
      return pkg.title.toLowerCase().includes(q)
        || pkg.author.toLowerCase().includes(q)
        || pkg.description.toLowerCase().includes(q);
    });

    if (!this.sortField) return filtered;

    const dir = this.sortDir === 'asc' ? 1 : -1;
    return [...filtered].sort((a, b) => {
      switch (this.sortField) {
        case 'title':    return a.title.localeCompare(b.title) * dir;
        case 'category': return a.category.localeCompare(b.category) * dir;
        case 'author':   return a.author.localeCompare(b.author) * dir;
        case 'stars':    return (a.stars - b.stars) * dir;
        default:         return 0;
      }
    });
  }

  public get upgradableCount(): number {
    return this.allInstalled.filter(p => p.is_upgradable).length;
  }

  public categoryCount(cat: string): number {
    return this.allInstalled.filter(p => p.category === cat).length;
  }

  public toggleSort(field: typeof this.sortField): void {
    if (this.sortField === field) {
      this.sortDir = this.sortDir === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortField = field;
      this.sortDir = field === 'stars' ? 'desc' : 'asc';
    }
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
    this.sub = this.store.packages.subscribe((packages: MagicMirrorPackage[]) => {
      this.allInstalled = packages.filter(p => p.is_installed);

      this.categories = ['all', ...this.allInstalled
        .map(pkg => pkg.category)
        .filter((cat, idx, self) => cat && self.indexOf(cat) === idx)
        .sort()
      ];

      this.loading = false;
    });
  }

  public ngOnDestroy(): void {
    this.sub.unsubscribe();
    window.removeEventListener('mousemove', this.onColMouseMove);
    window.removeEventListener('mouseup', this.onColMouseUp);
  }
}
