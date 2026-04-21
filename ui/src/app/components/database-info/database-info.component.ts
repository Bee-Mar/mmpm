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
  public upgradableItems = new Array<MagicMirrorPackage>();
  public selectedPackages = new Array<MagicMirrorPackage>();
  public selectedUpgrades = new Array<MagicMirrorPackage>();


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
  }

  public onUpdate(): void {
    this.loadingChange.emit(true);

    this.baseApi.get_('db/update').then((response: APIResponse) => {
      if (response.code === 200) {
        this.store.load();
        this.loadingChange.emit(false);

        this.msg.add({
          severity: 'success',
          summary: 'Update',
          detail: 'Completed check for available updates',
        });
      } else {
        this.msg.add({
          severity: 'error',
          summary: 'Update',
          detail: response.message,
        });
      }
    });
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
    const packages = this.selectedUpgrades.filter(
      (pkg: MagicMirrorPackage) =>
        pkg.title !== 'MMPM' && pkg.title !== 'MagicMirror',
    );
    this.loadingChange.emit(true);

    if (
      this.selectedUpgrades.findIndex(
        (pkg: MagicMirrorPackage) => pkg.title === 'MMPM',
      ) !== -1
    ) {
      this.baseApi.get_('mmpm/upgrade').then((response: APIResponse) => {
        if (response.code === 200) {
          this.msg.add({
            severity: 'success',
            summary: 'Upgrade',
            detail: 'MMPM has been upgraded',
          });
        } else {
          this.msg.add({
            severity: 'error',
            summary: 'Upgrade',
            detail: response.message,
          });
        }
      });
    }

    if (
      this.selectedUpgrades.findIndex(
        (pkg: MagicMirrorPackage) => pkg.title === 'MagicMirror',
      ) !== -1
    ) {
      const response = await this.mmApi.getUpgrade();

      if (response.code === 200) {
        this.msg.add({
          severity: 'success',
          summary: 'Upgrade',
          detail: 'MagicMirror has been upgraded',
        });
      } else {
        this.msg.add({
          severity: 'error',
          summary: 'Upgrade',
          detail: response.message,
        });
      }
    }

    this.selectedUpgrades = [];

    if (packages.length) {
      const response = await this.mmPkgApi.postUpgradePackages(packages);

      if (response.code === 200) {
        this.msg.add({
          severity: 'success',
          summary: 'Upgrade',
          detail: `${packages.length} packages have been upgraded`,
        });
      } else {
        this.msg.add({
          severity: 'error',
          summary: 'Upgrade',
          detail: response.message,
        });
      }
    }

    // the update endpoint will write out which packages have updates, and this needs
    // to get updated again following the actual upgrades
    const response = await this.baseApi.get_('db/update');

    if (response.code === 200) {
      this.msg.add({
        severity: 'success',
        summary: 'Upgrade',
        detail: 'Database updated to reflect changes',
      });
    } else {
      this.msg.add({
        severity: 'error',
        summary: 'Upgrade',
        detail: response.message,
      });
    }

    this.store.load();
    this.loadingChange.emit(false);
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
