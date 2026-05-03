import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject } from 'rxjs';
import { MagicMirrorPackage } from '@/models/magicmirror-package';
import { SharedStoreService } from '@/services/shared-store.service';
import { CurrentlyInstalledComponent } from './currently-installed.component';

function makePkg(overrides: Partial<MagicMirrorPackage> = {}): MagicMirrorPackage {
  return {
    title: 'test-module',
    author: 'Author',
    repository: 'https://github.com/test/repo',
    description: 'A test module',
    directory: '/modules/test-module',
    category: 'Utility',
    is_installed: true,
    is_upgradable: false,
    remote_details: { issues: 0, created: '', forks: 0 },
    stars: 10,
    last_updated: '2024-01-01',
    ...overrides,
  };
}

class MockSharedStoreService {
  packages = new BehaviorSubject<MagicMirrorPackage[]>([]);
}

describe('CurrentlyInstalledComponent', () => {
  let component: CurrentlyInstalledComponent;
  let fixture: ComponentFixture<CurrentlyInstalledComponent>;
  let mockStore: MockSharedStoreService;

  beforeEach(() => {
    mockStore = new MockSharedStoreService();

    TestBed.configureTestingModule({
      declarations: [CurrentlyInstalledComponent],
      providers: [{ provide: SharedStoreService, useValue: mockStore }],
      schemas: [NO_ERRORS_SCHEMA],
    });

    fixture = TestBed.createComponent(CurrentlyInstalledComponent);
    component = fixture.componentInstance;
    fixture.detectChanges(); // runs ngOnInit → subscribes to store.packages
  });

  afterEach(() => {
    component.ngOnDestroy();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  // ── ngOnInit / store subscription ─────────────────────────────────────────

  describe('store subscription', () => {
    it('populates allInstalled with installed packages only', () => {
      mockStore.packages.next([
        makePkg({ title: 'A', is_installed: true }),
        makePkg({ title: 'B', is_installed: false }),
      ]);
      expect(component.allInstalled.length).toBe(1);
      expect(component.allInstalled[0].title).toBe('A');
    });

    it('builds categories list from installed packages', () => {
      mockStore.packages.next([
        makePkg({ title: 'A', category: 'Weather', is_installed: true }),
        makePkg({ title: 'B', category: 'Finance', is_installed: true }),
      ]);
      expect(component.categories).toContain('all');
      expect(component.categories).toContain('Weather');
      expect(component.categories).toContain('Finance');
    });

    it('sets loading=false after receiving packages', () => {
      mockStore.packages.next([]);
      expect(component.loading).toBeFalse();
    });
  });

  // ── filteredPackages ──────────────────────────────────────────────────────

  describe('filteredPackages', () => {
    beforeEach(() => {
      component.allInstalled = [
        makePkg({ title: 'Alpha', author: 'Alice', category: 'Weather', stars: 50 }),
        makePkg({ title: 'Beta', author: 'Bob', category: 'Finance', stars: 20 }),
        makePkg({ title: 'Gamma', author: 'Alice', category: 'Weather', stars: 80 }),
      ];
    });

    it('returns all packages when no filter is active', () => {
      component.selectedCategory = 'all';
      component.searchQuery = '';
      expect(component.filteredPackages.length).toBe(3);
    });

    it('filters by category', () => {
      component.selectedCategory = 'Weather';
      component.searchQuery = '';
      const titles = component.filteredPackages.map(p => p.title);
      expect(titles).toEqual(jasmine.arrayContaining(['Alpha', 'Gamma']));
      expect(titles).not.toContain('Beta');
    });

    it('filters by title search query', () => {
      component.selectedCategory = 'all';
      component.searchQuery = 'alph';
      expect(component.filteredPackages.length).toBe(1);
      expect(component.filteredPackages[0].title).toBe('Alpha');
    });

    it('filters by author search query', () => {
      component.selectedCategory = 'all';
      component.searchQuery = 'alice';
      expect(component.filteredPackages.length).toBe(2);
    });

    it('is case-insensitive', () => {
      component.selectedCategory = 'all';
      component.searchQuery = 'ALPHA';
      expect(component.filteredPackages.length).toBe(1);
    });

    it('combines category and search filters', () => {
      component.selectedCategory = 'Weather';
      component.searchQuery = 'gamma';
      expect(component.filteredPackages.length).toBe(1);
      expect(component.filteredPackages[0].title).toBe('Gamma');
    });

    it('sorts by title ascending', () => {
      component.selectedCategory = 'all';
      component.sortField = 'title';
      component.sortDir = 'asc';
      const titles = component.filteredPackages.map(p => p.title);
      expect(titles).toEqual(['Alpha', 'Beta', 'Gamma']);
    });

    it('sorts by title descending', () => {
      component.selectedCategory = 'all';
      component.sortField = 'title';
      component.sortDir = 'desc';
      const titles = component.filteredPackages.map(p => p.title);
      expect(titles).toEqual(['Gamma', 'Beta', 'Alpha']);
    });

    it('sorts by stars', () => {
      component.selectedCategory = 'all';
      component.sortField = 'stars';
      component.sortDir = 'asc';
      const stars = component.filteredPackages.map(p => p.stars);
      expect(stars).toEqual([20, 50, 80]);
    });

    it('returns unsorted when sortField is null', () => {
      component.selectedCategory = 'all';
      component.sortField = null;
      expect(component.filteredPackages.length).toBe(3);
    });
  });

  // ── toggleSort ────────────────────────────────────────────────────────────

  describe('toggleSort', () => {
    it('sets sortField when previously null', () => {
      component.sortField = null;
      component.toggleSort('title');
      expect(component.sortField as string | null).toBe('title');
    });

    it('defaults to asc when setting a non-stars field', () => {
      component.sortField = null;
      component.toggleSort('title');
      expect(component.sortDir).toBe('asc');
    });

    it('defaults to desc when setting stars', () => {
      component.sortField = null;
      component.toggleSort('stars');
      expect(component.sortDir).toBe('desc');
    });

    it('flips asc → desc on the same field', () => {
      component.sortField = 'title';
      component.sortDir = 'asc';
      component.toggleSort('title');
      expect(component.sortDir).toBe('desc');
    });

    it('flips desc → asc on the same field', () => {
      component.sortField = 'title';
      component.sortDir = 'desc';
      component.toggleSort('title');
      expect(component.sortDir).toBe('asc');
    });

    it('resets direction when switching to a different field', () => {
      component.sortField = 'title';
      component.sortDir = 'desc';
      component.toggleSort('author');
      expect(component.sortField as string | null).toBe('author');
      expect(component.sortDir).toBe('asc');
    });
  });

  // ── categoryCount / upgradableCount ───────────────────────────────────────

  describe('categoryCount', () => {
    beforeEach(() => {
      component.allInstalled = [
        makePkg({ category: 'Weather' }),
        makePkg({ category: 'Weather' }),
        makePkg({ category: 'Finance' }),
      ];
    });

    it('counts packages in a given category', () => {
      expect(component.categoryCount('Weather')).toBe(2);
      expect(component.categoryCount('Finance')).toBe(1);
    });

    it('returns 0 for a category with no packages', () => {
      expect(component.categoryCount('Unknown')).toBe(0);
    });
  });

  describe('upgradableCount', () => {
    it('counts upgradable packages', () => {
      component.allInstalled = [
        makePkg({ is_upgradable: true }),
        makePkg({ is_upgradable: false }),
        makePkg({ is_upgradable: true }),
      ];
      expect(component.upgradableCount).toBe(2);
    });

    it('returns 0 when none are upgradable', () => {
      component.allInstalled = [makePkg({ is_upgradable: false })];
      expect(component.upgradableCount).toBe(0);
    });
  });

  // ── isSelected / toggleSelect ─────────────────────────────────────────────

  describe('isSelected', () => {
    const pkg = makePkg({ title: 'MyMod', repository: 'https://github.com/a/b' });

    it('returns false when package is not in selection', () => {
      component.selectedPackages = [];
      expect(component.isSelected(pkg)).toBeFalse();
    });

    it('returns true when package is in selection', () => {
      component.selectedPackages = [pkg];
      expect(component.isSelected(pkg)).toBeTrue();
    });

    it('matches on title and repository', () => {
      const differentRepo = makePkg({ title: 'MyMod', repository: 'https://github.com/other/repo' });
      component.selectedPackages = [pkg];
      expect(component.isSelected(differentRepo)).toBeFalse();
    });
  });

  describe('toggleSelect', () => {
    const pkgA = makePkg({ title: 'A', repository: 'https://github.com/a/a' });
    const pkgB = makePkg({ title: 'B', repository: 'https://github.com/b/b' });

    it('emits the package added to selection', () => {
      component.selectedPackages = [];
      const emitted: MagicMirrorPackage[][] = [];
      component.selectedPackagesChange.subscribe(v => emitted.push(v));

      component.toggleSelect(pkgA);
      expect(emitted[0]).toContain(pkgA);
    });

    it('emits the selection without a removed package', () => {
      component.selectedPackages = [pkgA, pkgB];
      const emitted: MagicMirrorPackage[][] = [];
      component.selectedPackagesChange.subscribe(v => emitted.push(v));

      component.toggleSelect(pkgA);
      expect(emitted[0]).not.toContain(pkgA);
      expect(emitted[0]).toContain(pkgB);
    });
  });

  // ── column resize ─────────────────────────────────────────────────────────

  describe('startColResize', () => {
    it('records the start position and initial width', () => {
      const event = new MouseEvent('mousedown', { clientX: 200, bubbles: true, cancelable: true });
      component.colWidths['title'] = 260;
      component.startColResize(event, 'title');
      expect((component as any).resizingCol).toBe('title');
      expect((component as any).resizeStartX).toBe(200);
      expect((component as any).resizeStartWidth).toBe(260);
    });

    it('prevents default to avoid text selection during resize', () => {
      const event = new MouseEvent('mousedown', { clientX: 0, bubbles: true, cancelable: true });
      spyOn(event, 'preventDefault');
      component.startColResize(event, 'title');
      expect(event.preventDefault).toHaveBeenCalled();
    });
  });
});
