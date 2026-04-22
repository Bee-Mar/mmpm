import { MagicMirrorPackage } from '@/models/magicmirror-package';
import { APIResponse } from '@/services/api/base-api';
import { MagicMirrorPackageAPI } from '@/services/api/magicmirror-package-api.service';
import { SharedStoreService } from '@/services/shared-store.service';
import {
  Component,
  OnInit,
  ViewChild,
  Input,
  Output,
  EventEmitter,
  OnDestroy,
  inject,
} from '@angular/core';
import { NgForm } from '@angular/forms';
import { MessageService } from 'primeng/api';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-custom-package-manager',
  templateUrl: './custom-package-manager.component.html',
  styleUrls: ['./custom-package-manager.component.scss'],
  providers: [MessageService],
  standalone: false,
})
export class CustomPackageManagerComponent implements OnInit, OnDestroy {
  private store = inject(SharedStoreService);
  private mmPkgApi = inject(MagicMirrorPackageAPI);
  private msg = inject(MessageService);

  private packagesSubscription: Subscription = new Subscription();

  @ViewChild('customPackageForm')
  public customPackageForm: NgForm;

  @Input() public loading: boolean;
  @Input() public view: 'add' | 'remove' | null = null;

  @Output() public loadingChange = new EventEmitter<boolean>(false);
  @Output() public openPanel = new EventEmitter<string>();
  @Output() public panelClosed = new EventEmitter<void>();

  public showMenu = false;
  public selectedCustomPackages = new Array<MagicMirrorPackage>();
  public customPackages = new Array<MagicMirrorPackage>();
  public customPackage: MagicMirrorPackage = this.clearCustomPackage();


  public ngOnInit(): void {
    this.packagesSubscription = this.store.packages.subscribe(
      (packages: Array<MagicMirrorPackage>) => {
        this.customPackages = packages.filter(
          (pkg: MagicMirrorPackage) => pkg.category === 'Custom Packages',
        );
      },
    );
  }

  public ngOnDestroy(): void {
    this.packagesSubscription.unsubscribe();
  }

  public clearCustomPackage(): MagicMirrorPackage {
    return {
      title: '',
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

  public onAddMmPkg(): void {
    this.loadingChange.emit(true);

    this.mmPkgApi
      .postAddMmPkg(this.customPackage)
      .then((response: APIResponse) => {
        this.reset();
        this.store.load();
        this.panelClosed.emit();

        if (response.code === 200) {
          this.msg.add({
            severity: 'success',
            summary: 'Add Custom Package',
            detail: `Successfully added ${this.customPackage.title} to database`,
          });
        } else {
          this.msg.add({
            severity: 'error',
            summary: 'Add Custom Package',
            detail: response.message,
          });
        }
      })
      .catch((error) => {
        this.reset();
        this.store.load();
        console.log(error);
      });
  }

  public onRemoveMmPkg(): void {
    this.loadingChange.emit(true);

    this.mmPkgApi
      .postRemoveMmPkgs(this.selectedCustomPackages)
      .then((response: APIResponse) => {
        this.reset();
        this.store.load();
        this.panelClosed.emit();

        const success = response.message.success as Array<MagicMirrorPackage>;
        const failure = response.message.failure as Array<MagicMirrorPackage>;

        if (success.length) {
          this.msg.add({
            severity: 'success',
            summary: 'Remove Custom Packages',
            detail: `Successfully removed custom packages: ${success.map((pkg) => pkg.title).join(', ')}`,
          });
        }

        if (failure.length) {
          this.msg.add({
            severity: 'error',
            summary: 'Remove Custom Packages',
            detail: `Failed to remove custom packages: ${failure.map((pkg) => pkg.title).join(', ')}. See logs for details.`,
          });
        }
      })
      .catch((error) => {
        this.reset();
        this.store.load();
        console.log(error);
      });
  }

  public reset(): void {
    this.customPackage = this.clearCustomPackage();
    this.customPackageForm.reset();
  }
}
