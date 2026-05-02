import { MagicMirrorPackage, RemotePackageDetails } from '@/models/magicmirror-package';
import { Component, Input, Output, EventEmitter, inject } from '@angular/core';
import { APIResponse } from '@/services/api/base-api';
import { MagicMirrorPackageAPI } from '@/services/api/magicmirror-package-api.service';
import { SharedStoreService } from '@/services/shared-store.service';
import { MessageService } from 'primeng/api';
import { getModuleIcon, ModuleIcon } from '@/utils/module-icon';

@Component({
  selector: 'app-package-details-viewer',
  templateUrl: './package-details-viewer.component.html',
  styleUrls: ['./package-details-viewer.component.scss'],
  providers: [MessageService],
  standalone: false,
})
export class PackageDetailsViewerComponent {
  private mmPkgApi = inject(MagicMirrorPackageAPI);
  private store = inject(SharedStoreService);
  private msg = inject(MessageService);

  @Input() selectedPackage: MagicMirrorPackage | null = null;
  @Input() selectedPackages: MagicMirrorPackage[] = [];
  @Output() selectedPackagesChange = new EventEmitter<MagicMirrorPackage[]>();
  @Output() closePanel = new EventEmitter<void>();

  public loadingRemote = false;
  public upgrading = false;

  public get isQueued(): boolean {
    if (!this.selectedPackage) return false;
    return this.selectedPackages.some(
      p => p.title === this.selectedPackage!.title && p.repository === this.selectedPackage!.repository
    );
  }

  public toggleQueue(): void {
    if (!this.selectedPackage) return;
    const next = this.isQueued
      ? this.selectedPackages.filter(
          p => !(p.title === this.selectedPackage!.title && p.repository === this.selectedPackage!.repository)
        )
      : [...this.selectedPackages, this.selectedPackage];
    this.selectedPackagesChange.emit(next);
  }

  public loadRemoteDetails(): void {
    if (!this.selectedPackage || this.selectedPackage.remote_details) return;

    this.loadingRemote = true;
    this.mmPkgApi.postDetails(this.selectedPackage).then((response: APIResponse) => {
      if (response.code === 200 && this.selectedPackage) {
        this.selectedPackage.remote_details = response.message as RemotePackageDetails;
      }
      this.loadingRemote = false;
    }).catch(() => {
      this.loadingRemote = false;
    });
  }

  public onUpgrade(): void {
    if (!this.selectedPackage || this.upgrading) return;
    this.upgrading = true;
    this.mmPkgApi.postUpgradePackages([this.selectedPackage]).then((response: APIResponse) => {
      this.upgrading = false;
      const failure = response.message?.failure?.[0];
      if (response.code === 200 && !failure) {
        this.msg.add({ severity: 'success', summary: 'Upgrade', detail: `${this.selectedPackage!.title} upgraded successfully` });
        this.store.load();
      } else {
        const detail = failure?.error || response.message || 'Upgrade failed';
        this.msg.add({ severity: 'error', summary: `Failed to upgrade ${this.selectedPackage!.title}`, detail, life: 8000 });
      }
    }).catch(() => {
      this.upgrading = false;
      this.msg.add({ severity: 'error', summary: 'Upgrade', detail: 'Upgrade failed' });
    });
  }

  public openRepo(): void {
    if (this.selectedPackage?.repository) {
      window.open(this.selectedPackage.repository, '_blank');
    }
  }

  public get moduleIcon(): ModuleIcon | null {
    return this.selectedPackage ? getModuleIcon(this.selectedPackage) : null;
  }
}
