import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { BehaviorSubject } from 'rxjs';
import { ConfirmationService, MessageService } from 'primeng/api';
import { BaseAPI } from '@/services/api/base-api';
import { MagicMirrorPackageAPI } from '@/services/api/magicmirror-package-api.service';
import { MagicMirrorAPI } from '@/services/api/magicmirror-api.service';
import { SharedStoreService } from '@/services/shared-store.service';
import { MagicMirrorPackage } from '@/models/magicmirror-package';
import { DatabaseInfo } from '@/models/database-info';
import { UpgradableDetails } from '@/models/upgradable-details';
import { MMPMEnv } from '@/models/mmpm-env';
import { DatabaseInfoComponent } from './database-info.component';

function makePkg(title: string): MagicMirrorPackage {
  return {
    title,
    author: 'Author',
    repository: `https://github.com/test/${title}`,
    description: 'A test module',
    directory: `/modules/${title}`,
    category: 'Test',
    is_installed: true,
    is_upgradable: true,
    remote_details: { issues: 0, created: '', forks: 0 },
    stars: 5,
    last_updated: '2024-01-01',
  };
}

class MockSharedStoreService {
  dbInfo    = new BehaviorSubject<DatabaseInfo>({});
  upgradable = new BehaviorSubject<UpgradableDetails>({ mmpm: false, MagicMirror: false, packages: [] });
  packages  = new BehaviorSubject<MagicMirrorPackage[]>([]);
  env       = new BehaviorSubject<MMPMEnv>({
    MMPM_IS_DOCKER_IMAGE: false,
    MMPM_LOG_LEVEL: '',
    MMPM_MAGICMIRROR_DOCKER_COMPOSE_FILE: '',
    MMPM_MAGICMIRROR_PM2_PROCESS_NAME: '',
    MMPM_MAGICMIRROR_ROOT: '',
    MMPM_MAGICMIRROR_URI: '',
  });
  load = jasmine.createSpy('load');
}

describe('DatabaseInfoComponent', () => {
  let component: DatabaseInfoComponent;
  let fixture: ComponentFixture<DatabaseInfoComponent>;
  let mockBaseAPI: jasmine.SpyObj<BaseAPI>;
  let mockMmPkgApi: jasmine.SpyObj<MagicMirrorPackageAPI>;
  let mockMmApi: jasmine.SpyObj<MagicMirrorAPI>;
  let mockStore: MockSharedStoreService;

  beforeEach(() => {
    mockBaseAPI = jasmine.createSpyObj('BaseAPI', ['get_', 'route', 'headers']);
    mockBaseAPI.get_.and.returnValue(Promise.resolve({ code: 200, message: '' }));

    mockMmPkgApi = jasmine.createSpyObj('MagicMirrorPackageAPI', ['get_', 'getPackages', 'postUpgradePackages']);
    mockMmPkgApi.postUpgradePackages.and.returnValue(
      Promise.resolve({ code: 200, message: { success: [], failure: [] } })
    );

    mockMmApi = jasmine.createSpyObj('MagicMirrorAPI', ['getStatus', 'getUpgrade']);
    mockMmApi.getUpgrade.and.returnValue(Promise.resolve({ code: 200, message: '' }));

    mockStore = new MockSharedStoreService();

    TestBed.configureTestingModule({
      declarations: [DatabaseInfoComponent],
      providers: [
        { provide: BaseAPI,               useValue: mockBaseAPI },
        { provide: MagicMirrorPackageAPI, useValue: mockMmPkgApi },
        { provide: MagicMirrorAPI,        useValue: mockMmApi },
        { provide: SharedStoreService,    useValue: mockStore },
        { provide: MessageService,        useValue: jasmine.createSpyObj('MessageService', ['add']) },
        { provide: ConfirmationService,   useValue: jasmine.createSpyObj('ConfirmationService', ['confirm']) },
      ],
      schemas: [NO_ERRORS_SCHEMA],
    });

    fixture = TestBed.createComponent(DatabaseInfoComponent);
    component = fixture.componentInstance;
    component.loading = false;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  // ── upgradable store subscription ─────────────────────────────────────────

  describe('upgradable store subscription', () => {
    it('populates upgradableItems from packages', () => {
      const pkg = makePkg('MMM-Test');
      mockStore.upgradable.next({ mmpm: false, MagicMirror: false, packages: [pkg] });
      expect(component.upgradableItems).toContain(pkg);
    });

    it('appends MMPM dummy entry when mmpm=true', () => {
      mockStore.upgradable.next({ mmpm: true, MagicMirror: false, packages: [] });
      expect(component.upgradableItems.some(p => p.title === 'MMPM')).toBeTrue();
    });

    it('appends MagicMirror dummy entry when MagicMirror=true', () => {
      mockStore.upgradable.next({ mmpm: false, MagicMirror: true, packages: [] });
      expect(component.upgradableItems.some(p => p.title === 'MagicMirror')).toBeTrue();
    });

    it('sets upgradesAvailable when packages are present', () => {
      mockStore.upgradable.next({ mmpm: false, MagicMirror: false, packages: [makePkg('A')] });
      expect(component.upgradesAvailable).toBeTrue();
    });

    it('sets upgradesAvailable when mmpm=true', () => {
      mockStore.upgradable.next({ mmpm: true, MagicMirror: false, packages: [] });
      expect(component.upgradesAvailable).toBeTrue();
    });

    it('clears upgradesAvailable when nothing to upgrade', () => {
      mockStore.upgradable.next({ mmpm: false, MagicMirror: false, packages: [] });
      expect(component.upgradesAvailable).toBeFalse();
    });
  });

  // ── isUpgradeSelected / toggleUpgrade ────────────────────────────────────

  describe('isUpgradeSelected', () => {
    it('returns false when package is not in selectedUpgrades', () => {
      component.selectedUpgrades = [];
      expect(component.isUpgradeSelected(makePkg('A'))).toBeFalse();
    });

    it('returns true when package is in selectedUpgrades', () => {
      const pkg = makePkg('A');
      component.selectedUpgrades = [pkg];
      expect(component.isUpgradeSelected(pkg)).toBeTrue();
    });

    it('matches by title', () => {
      component.selectedUpgrades = [makePkg('A')];
      expect(component.isUpgradeSelected(makePkg('B'))).toBeFalse();
    });
  });

  describe('toggleUpgrade', () => {
    it('adds package to selectedUpgrades when not already selected', () => {
      const pkg = makePkg('A');
      component.selectedUpgrades = [];
      component.toggleUpgrade(pkg);
      expect(component.selectedUpgrades).toContain(pkg);
    });

    it('removes package from selectedUpgrades when already selected', () => {
      const pkg = makePkg('A');
      component.selectedUpgrades = [pkg];
      component.toggleUpgrade(pkg);
      expect(component.selectedUpgrades).not.toContain(pkg);
    });

    it('preserves other selections when removing one', () => {
      const pkgA = makePkg('A');
      const pkgB = makePkg('B');
      component.selectedUpgrades = [pkgA, pkgB];
      component.toggleUpgrade(pkgA);
      expect(component.selectedUpgrades).toContain(pkgB);
    });
  });

  // ── Select All ────────────────────────────────────────────────────────────

  describe('allUpgradesSelected', () => {
    it('returns false when upgradableItems is empty', () => {
      component.upgradableItems = [];
      component.selectedUpgrades = [];
      expect(component.allUpgradesSelected).toBeFalse();
    });

    it('returns false when no items are selected', () => {
      component.upgradableItems = [makePkg('A'), makePkg('B')];
      component.selectedUpgrades = [];
      expect(component.allUpgradesSelected).toBeFalse();
    });

    it('returns false when only some items are selected', () => {
      const pkgA = makePkg('A');
      const pkgB = makePkg('B');
      component.upgradableItems = [pkgA, pkgB];
      component.selectedUpgrades = [pkgA];
      expect(component.allUpgradesSelected).toBeFalse();
    });

    it('returns true when every item is selected', () => {
      const pkgA = makePkg('A');
      const pkgB = makePkg('B');
      component.upgradableItems = [pkgA, pkgB];
      component.selectedUpgrades = [pkgA, pkgB];
      expect(component.allUpgradesSelected).toBeTrue();
    });
  });

  describe('someUpgradesSelected', () => {
    it('returns false when no items are selected', () => {
      component.upgradableItems = [makePkg('A'), makePkg('B')];
      component.selectedUpgrades = [];
      expect(component.someUpgradesSelected).toBeFalse();
    });

    it('returns true when a subset of items is selected', () => {
      const pkgA = makePkg('A');
      const pkgB = makePkg('B');
      component.upgradableItems = [pkgA, pkgB];
      component.selectedUpgrades = [pkgA];
      expect(component.someUpgradesSelected).toBeTrue();
    });

    it('returns true when all items are selected', () => {
      const pkg = makePkg('A');
      component.upgradableItems = [pkg];
      component.selectedUpgrades = [pkg];
      expect(component.someUpgradesSelected).toBeTrue();
    });
  });

  describe('toggleSelectAll', () => {
    it('selects all items when none are selected', () => {
      const pkgA = makePkg('A');
      const pkgB = makePkg('B');
      component.upgradableItems = [pkgA, pkgB];
      component.selectedUpgrades = [];
      component.toggleSelectAll();
      expect(component.selectedUpgrades.length).toBe(2);
      expect(component.selectedUpgrades).toContain(pkgA);
      expect(component.selectedUpgrades).toContain(pkgB);
    });

    it('selects all items when only some are selected', () => {
      const pkgA = makePkg('A');
      const pkgB = makePkg('B');
      component.upgradableItems = [pkgA, pkgB];
      component.selectedUpgrades = [pkgA];
      component.toggleSelectAll();
      expect(component.selectedUpgrades.length).toBe(2);
    });

    it('deselects all items when all are already selected', () => {
      const pkgA = makePkg('A');
      const pkgB = makePkg('B');
      component.upgradableItems = [pkgA, pkgB];
      component.selectedUpgrades = [pkgA, pkgB];
      component.toggleSelectAll();
      expect(component.selectedUpgrades.length).toBe(0);
    });

    it('does nothing to selection when upgradableItems is empty', () => {
      component.upgradableItems = [];
      component.selectedUpgrades = [];
      component.toggleSelectAll();
      expect(component.selectedUpgrades.length).toBe(0);
    });
  });

  // ── upgrade() – immediate visual feedback ─────────────────────────────────

  describe('upgrade() status tracking', () => {
    let pkgA: MagicMirrorPackage;
    let pkgB: MagicMirrorPackage;

    beforeEach(() => {
      pkgA = makePkg('MMM-Alpha');
      pkgB = makePkg('MMM-Beta');
      component.upgradableItems = [pkgA, pkgB];
      component.selectedUpgrades = [pkgA, pkgB];
    });

    it('sets isRunning to true immediately when upgrade starts', fakeAsync(() => {
      component.upgrade();
      expect(component.isRunning).toBeTrue();
      tick(1400);
    }));

    it('sets all selected packages to working in opStatus immediately', fakeAsync(() => {
      component.upgrade();
      expect(component.opStatus.get('MMM-Alpha')).toBe('working');
      expect(component.opStatus.get('MMM-Beta')).toBe('working');
      tick(1400);
    }));

    it('marks packages as done when API reports success', fakeAsync(() => {
      mockMmPkgApi.postUpgradePackages.and.returnValue(Promise.resolve({
        code: 200,
        message: { success: [pkgA, pkgB], failure: [] },
      }));
      component.upgrade();
      tick(0);
      expect(component.opStatus.get('MMM-Alpha')).toBe('done');
      expect(component.opStatus.get('MMM-Beta')).toBe('done');
      tick(1400);
    }));

    it('marks packages as failed when API reports failure', fakeAsync(() => {
      mockMmPkgApi.postUpgradePackages.and.returnValue(Promise.resolve({
        code: 200,
        message: {
          success: [],
          failure: [
            { title: 'MMM-Alpha', error: 'git error' },
            { title: 'MMM-Beta',  error: 'git error' },
          ],
        },
      }));
      component.upgrade();
      tick(0);
      expect(component.opStatus.get('MMM-Alpha')).toBe('failed');
      expect(component.opStatus.get('MMM-Beta')).toBe('failed');
      tick(1400);
    }));

    it('marks individual packages done or failed per API response', fakeAsync(() => {
      mockMmPkgApi.postUpgradePackages.and.returnValue(Promise.resolve({
        code: 200,
        message: {
          success: [pkgA],
          failure: [{ title: 'MMM-Beta', error: 'git error' }],
        },
      }));
      component.upgrade();
      tick(0);
      expect(component.opStatus.get('MMM-Alpha')).toBe('done');
      expect(component.opStatus.get('MMM-Beta')).toBe('failed');
      tick(1400);
    }));

    it('resets isRunning to false after the post-upgrade delay', fakeAsync(() => {
      component.upgrade();
      tick(1400);
      expect(component.isRunning).toBeFalse();
    }));

    it('clears opStatus after the post-upgrade delay', fakeAsync(() => {
      component.upgrade();
      tick(1400);
      expect(component.opStatus.size).toBe(0);
    }));

    it('clears selectedUpgrades during the upgrade', fakeAsync(() => {
      component.upgrade();
      tick(0);
      expect(component.selectedUpgrades).toEqual([]);
      tick(1400);
    }));

    it('calls postUpgradePackages excluding MMPM and MagicMirror entries', fakeAsync(() => {
      component.upgrade();
      tick(1400);
      expect(mockMmPkgApi.postUpgradePackages).toHaveBeenCalledWith([pkgA, pkgB]);
    }));

    it('calls store.load() after upgrades complete', fakeAsync(() => {
      component.upgrade();
      tick(0);
      expect(mockStore.load).toHaveBeenCalled();
      tick(1400);
    }));
  });

  // ── upgrade() – MagicMirror status tracking ───────────────────────────────

  describe('upgrade() MagicMirror status', () => {
    const mmDummy = { ...makePkg('MagicMirror'), title: 'MagicMirror' };

    beforeEach(() => {
      component.upgradableItems = [mmDummy];
      component.selectedUpgrades = [mmDummy];
    });

    it('sets MagicMirror to working immediately', fakeAsync(() => {
      component.upgrade();
      expect(component.opStatus.get('MagicMirror')).toBe('working');
      tick(1400);
    }));

    it('marks MagicMirror as done when getUpgrade succeeds', fakeAsync(() => {
      mockMmApi.getUpgrade.and.returnValue(Promise.resolve({ code: 200, message: '' }));
      component.upgrade();
      tick(0);
      expect(component.opStatus.get('MagicMirror')).toBe('done');
      tick(1400);
    }));

    it('marks MagicMirror as failed when getUpgrade returns non-200', fakeAsync(() => {
      mockMmApi.getUpgrade.and.returnValue(Promise.resolve({ code: 500, message: 'error' }));
      component.upgrade();
      tick(0);
      expect(component.opStatus.get('MagicMirror')).toBe('failed');
      tick(1400);
    }));

    it('does not call postUpgradePackages when only MagicMirror is selected', fakeAsync(() => {
      component.upgrade();
      tick(1400);
      expect(mockMmPkgApi.postUpgradePackages).not.toHaveBeenCalled();
    }));
  });
});
