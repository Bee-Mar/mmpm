import { MagicMirrorPackage, RemotePackageDetails } from '@/models/magicmirror-package';
import { Component, Input, Output, EventEmitter, inject } from '@angular/core';
import { APIResponse } from '@/services/api/base-api';
import { MagicMirrorPackageAPI } from '@/services/api/magicmirror-package-api.service';
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
  private msg = inject(MessageService);

  @Input() selectedPackage: MagicMirrorPackage | null = null;
  @Input() selectedPackages: MagicMirrorPackage[] = [];
  @Output() selectedPackagesChange = new EventEmitter<MagicMirrorPackage[]>();
  @Output() closePanel = new EventEmitter<void>();

  public loadingRemote = false;

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

  public openRepo(): void {
    if (this.selectedPackage?.repository) {
      window.open(this.selectedPackage.repository, '_blank');
    }
  }

  public get moduleIcon(): ModuleIcon | null {
    return this.selectedPackage ? getModuleIcon(this.selectedPackage) : null;
  }
}
