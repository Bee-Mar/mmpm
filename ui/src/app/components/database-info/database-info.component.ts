import {
  Component,
  Input,
  OnDestroy,
  OnInit,
  Output,
  EventEmitter,
  inject,
} from '@angular/core';
import { DatabaseInfo } from '@/models/database-info';
import { Subscription } from 'rxjs';
import { APIResponse, BaseAPI } from '@/services/api/base-api';
import { SharedStoreService } from '@/services/shared-store.service';
import { MagicMirrorPackage } from '@/models/magicmirror-package';
import { UpgradableDetails } from '@/models/upgradable-details';
import { MagicMirrorPackageAPI } from '@/services/api/magicmirror-package-api.service';
import { MagicMirrorAPI } from '@/services/api/magicmirror-api.service';
import { ConfirmationService, MessageService } from 'primeng/api';

@Component({
  selector: 'app-database-info',
  templateUrl: './database-info.component.html',
  styleUrls: ['./database-info.component.scss'],
  providers: [MessageService, ConfirmationService],
  standalone: false,
})
export class DatabaseInfoComponent implements OnInit, OnDestroy {
  private baseApi = inject(BaseAPI);
  private mmPkgApi = inject(MagicMirrorPackageAPI);
  private store = inject(SharedStoreService);
  private mmApi = inject(MagicMirrorAPI);
  private msg = inject(MessageService);
  private confirmation = inject(ConfirmationService);

  private dbInfoSubscription: Subscription = new Subscription();
  private upgradableSubscription: Subscription = new Subscription();

  @Input() public loading: boolean;
  @Input() public view: 'info' | 'upgrades' | null = null;

  @Output() public loadingChange = new EventEmitter<boolean>(false);
  @Output() public openPanel = new EventEmitter<string>();
  @Output() public panelClosed = new EventEmitter<void>();

  public version = '';
  public dbInfo: DatabaseInfo | undefined;
  public showMenu = false;
  public upgradesAvailable = false;
  public updating = false;
  public updateDone = false;
  public upgradableItems = new Array<MagicMirrorPackage>();
  public selectedPackages = new Array<MagicMirrorPackage>();
  public selectedUpgrades = new Array<MagicMirrorPackage>();
  public opStatus: Map<string, 'working' | 'done' | 'failed'> = new Map();
  public isRunning = false;
  private updateDoneTimer: ReturnType<typeof setTimeout> | null = null;


  public ngOnInit(): void {
    this.baseApi.get_('mmpm/version').then((response: APIResponse) => {
      this.version = response.message;
    });

    this.dbInfoSubscription = this.store.dbInfo.subscribe(
      (info: DatabaseInfo) => {
        this.dbInfo = info;
      },
    );

    this.upgradableSubscription = this.store.upgradable.subscribe(
      (upgradable: UpgradableDetails) => {
        this.upgradableItems = [];
        this.upgradesAvailable = Boolean(
          upgradable &&
          (upgradable.mmpm ||
            upgradable.MagicMirror ||
            upgradable.packages.length),
        );

        this.upgradableItems.push(...upgradable.packages);

        if (upgradable.mmpm) {
          this.upgradableItems.push(this.dummyPackage('MMPM'));
        }

        if (upgradable.MagicMirror) {
          this.upgradableItems.push(this.dummyPackage('MagicMirror'));
        }

      },
    );
  }

  public ngOnDestroy(): void {
    this.dbInfoSubscription.unsubscribe();
    this.upgradableSubscription.unsubscribe();
    if (this.updateDoneTimer) clearTimeout(this.updateDoneTimer);
  }

  public onUpdate(): void {
    this.updating = true;
    this.updateDone = false;
    this.loadingChange.emit(true);

    this.baseApi.get_('db/update').then((response: APIResponse) => {
      this.updating = false;
      this.loadingChange.emit(false);

      if (response.code === 200) {
        this.store.load();
        this.updateDone = true;
        if (this.updateDoneTimer) clearTimeout(this.updateDoneTimer);
        this.updateDoneTimer = setTimeout(() => { this.updateDone = false; }, 2500);

        this.msg.add({
          severity: 'success',
          summary: 'Database',
          detail: 'Database updated successfully',
        });
      } else {
        this.msg.add({
          severity: 'error',
          summary: 'Database',
          detail: response.message,
        });
      }
    }).catch(() => {
      this.updating = false;
      this.loadingChange.emit(false);
    });
  }

  public isUpgradeSelected(pkg: MagicMirrorPackage): boolean {
    return this.selectedUpgrades.some(p => p.title === pkg.title);
  }

  public get allUpgradesSelected(): boolean {
    return this.upgradableItems.length > 0 && this.upgradableItems.every(p => this.isUpgradeSelected(p));
  }

  public get someUpgradesSelected(): boolean {
    return this.upgradableItems.some(p => this.isUpgradeSelected(p));
  }

  public toggleSelectAll(): void {
    this.selectedUpgrades = this.allUpgradesSelected ? [] : [...this.upgradableItems];
  }

  public toggleUpgrade(pkg: MagicMirrorPackage): void {
    this.selectedUpgrades = this.isUpgradeSelected(pkg)
      ? this.selectedUpgrades.filter(p => p.title !== pkg.title)
      : [...this.selectedUpgrades, pkg];
  }

  public onUpgrade() {
    let message = 'Are you sure you want to upgrade the selected packages?';

    if (
      this.selectedUpgrades.findIndex(
        (pkg: MagicMirrorPackage) => pkg.title === 'MMPM',
      ) !== -1
    ) {
      message += `  <strong>NOTE</strong>: After upgrading MMPM, execute <code>mmpm ui reinstall -y</code>`;
    }

    this.confirmation.confirm({
      message: message,
      header: 'Confirmation',
      icon: 'pi pi-exclamation-triangle',
      accept: () => {
        this.upgrade();
      },
      reject: () => {
        return;
      },
    });
  }

  async upgrade() {
    const toUpgrade = [...this.selectedUpgrades];
    const packages = toUpgrade.filter(p => p.title !== 'MMPM' && p.title !== 'MagicMirror');

    this.isRunning = true;
    this.opStatus = new Map(toUpgrade.map(p => [p.title, 'working']));
    this.loadingChange.emit(true);

    if (toUpgrade.find(p => p.title === 'MMPM')) {
      // fire-and-forget: MMPM restarts itself mid-upgrade
      this.baseApi.get_('mmpm/upgrade').then((response: APIResponse) => {
        this.setOpStatus('MMPM', response.code === 200 ? 'done' : 'failed');
        this.msg.add(response.code === 200
          ? { severity: 'success', summary: 'Upgrade', detail: 'MMPM has been upgraded' }
          : { severity: 'error', summary: 'Upgrade', detail: response.message });
      });
    }

    if (toUpgrade.find(p => p.title === 'MagicMirror')) {
      const response = await this.mmApi.getUpgrade();
      this.setOpStatus('MagicMirror', response.code === 200 ? 'done' : 'failed');
      this.msg.add(response.code === 200
        ? { severity: 'success', summary: 'Upgrade', detail: 'MagicMirror has been upgraded' }
        : { severity: 'error', summary: 'Upgrade', detail: response.message });
    }

    this.selectedUpgrades = [];

    if (packages.length) {
      const response = await this.mmPkgApi.postUpgradePackages(packages);
      const succeeded: MagicMirrorPackage[] = response.message?.success ?? [];
      const failures: { title: string; error: string }[] = response.message?.failure ?? [];

      succeeded.forEach(p => this.setOpStatus(p.title, 'done'));
      failures.forEach(f => this.setOpStatus(f.title, 'failed'));

      if (response.code === 200 && succeeded.length > 0) {
        this.msg.add({
          severity: 'success',
          summary: 'Upgrade',
          detail: `${succeeded.length} package${succeeded.length === 1 ? '' : 's'} upgraded successfully`,
        });
      }
      for (const f of failures) {
        this.msg.add({ severity: 'error', summary: `Failed to upgrade ${f.title}`, detail: f.error, life: 8000 });
      }
    }

    // the update endpoint will write out which packages have updates, and this needs
    // to get updated again following the actual upgrades
    const dbResponse = await this.baseApi.get_('db/update');
    if (dbResponse.code === 200) {
      this.msg.add({ severity: 'success', summary: 'Upgrade', detail: 'Database updated to reflect changes' });
    } else {
      this.msg.add({ severity: 'error', summary: 'Upgrade', detail: dbResponse.message });
    }

    this.store.load();

    await new Promise<void>(resolve => setTimeout(resolve, 1400));
    this.opStatus = new Map();
    this.isRunning = false;
    this.loadingChange.emit(false);
  }

  private setOpStatus(title: string, status: 'working' | 'done' | 'failed'): void {
    this.opStatus = new Map(this.opStatus).set(title, status);
  }

  private dummyPackage(title: string): MagicMirrorPackage {
    return {
      title: title,
      repository: '',
      author: '',
      description: '',
      directory: '',
      is_installed: false,
      is_upgradable: false,
      category: 'Custom Packages',
      stars: 0,
      last_updated: '',
      remote_details: {
        forks: 0,
        issues: 0,
        created: '',
      },
    };
  }
}
