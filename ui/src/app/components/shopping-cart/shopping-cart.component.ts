import { MagicMirrorPackage } from '@/models/magicmirror-package';
import { MagicMirrorPackageAPI } from '@/services/api/magicmirror-package-api.service';
import { SharedStoreService } from '@/services/shared-store.service';
import { Component, Input, Output, EventEmitter, inject } from '@angular/core';
import { ConfirmationService, MessageService } from 'primeng/api';

type OpStatus = 'pending' | 'working' | 'done' | 'failed';

@Component({
  selector: 'app-shopping-cart',
  templateUrl: './shopping-cart.component.html',
  styleUrls: ['./shopping-cart.component.scss'],
  providers: [MessageService, ConfirmationService],
  standalone: false,
})
export class ShoppingCartComponent {
  private store = inject(SharedStoreService);
  private mmPkgApi = inject(MagicMirrorPackageAPI);
  private msg = inject(MessageService);
  private confirmation = inject(ConfirmationService);

  @Input()
  public selectedPackages: Array<MagicMirrorPackage>;

  @Output()
  public selectedPackagesChange = new EventEmitter<Array<MagicMirrorPackage>>();

  @Input()
  public loading: boolean;

  @Output()
  public loadingChange = new EventEmitter<boolean>(false);

  public opStatus: Map<string, OpStatus> = new Map();
  public isRunning = false;

  public get installs(): MagicMirrorPackage[] {
    return this.selectedPackages.filter(p => !p.is_installed);
  }

  public get removals(): MagicMirrorPackage[] {
    return this.selectedPackages.filter(p => p.is_installed);
  }

  public pkgKey(pkg: MagicMirrorPackage): string {
    return pkg.repository || pkg.title;
  }

  public onCheckout(): void {
    this.confirmation.confirm({
      message: 'Are you sure you want to install/remove the selected packages?',
      header: 'Confirmation',
      icon: 'pi pi-exclamation-triangle',
      accept: () => {
        this.checkout();
      },
      reject: () => {
        return;
      },
    });
  }

  async checkout() {
    if (!this.selectedPackages?.length) return;

    const toRemove = this.selectedPackages.filter(p => p.is_installed);
    const toInstall = this.selectedPackages.filter(p => !p.is_installed);

    this.isRunning = true;
    this.opStatus = new Map(this.selectedPackages.map(p => [this.pkgKey(p), 'pending' as OpStatus]));
    this.loadingChange.emit(true);

    for (const pkg of toRemove) {
      this.setStatus(pkg, 'working');
      const response = await this.mmPkgApi.postRemovePackages([pkg]);
      const success = response.message.success as Array<MagicMirrorPackage>;
      this.setStatus(pkg, success.length ? 'done' : 'failed');
      if (!success.length) {
        this.msg.add({ severity: 'error', summary: 'Remove', detail: `Failed to remove ${pkg.title}. See logs for details.` });
      }
    }

    for (const pkg of toInstall) {
      this.setStatus(pkg, 'working');
      const response = await this.mmPkgApi.postInstallPackages([pkg]);
      const success = response.message.success as Array<MagicMirrorPackage>;
      this.setStatus(pkg, success.length ? 'done' : 'failed');
      if (!success.length) {
        this.msg.add({ severity: 'error', summary: 'Install', detail: `Failed to install ${pkg.title}. See logs for details.` });
      }
    }

    this.store.load();

    await new Promise<void>(resolve => setTimeout(resolve, 1400));

    this.selectedPackagesChange.emit([]);
    this.opStatus = new Map();
    this.isRunning = false;
    this.loadingChange.emit(false);
  }

  private setStatus(pkg: MagicMirrorPackage, status: OpStatus): void {
    this.opStatus = new Map(this.opStatus).set(this.pkgKey(pkg), status);
  }
}
