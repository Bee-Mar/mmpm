import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject } from 'rxjs';
import { MessageService } from 'primeng/api';
import { MagicMirrorPackageAPI } from '@/services/api/magicmirror-package-api.service';
import { SharedStoreService } from '@/services/shared-store.service';
import { PackageDetailsViewerComponent } from './package-details-viewer.component';

class MockSharedStoreService {
  packages = new BehaviorSubject<any[]>([]);
  load = jasmine.createSpy('load');
}

describe('PackageDetailsViewerComponent', () => {
  let component: PackageDetailsViewerComponent;
  let fixture: ComponentFixture<PackageDetailsViewerComponent>;
  let mockMmPkgApi: jasmine.SpyObj<MagicMirrorPackageAPI>;

  const pkg = {
    title: 'MMM-Test',
    author: 'tester',
    repository: 'https://github.com/tester/MMM-Test',
    description: 'A test module',
    directory: 'MMM-Test',
    category: 'Test',
    is_installed: false,
    is_upgradable: false,
    remote_details: null as any,
    stars: 5,
    last_updated: '2024-01-01',
  };

  beforeEach(() => {
    mockMmPkgApi = jasmine.createSpyObj('MagicMirrorPackageAPI', [
      'postDetails',
      'postUpgradePackages',
    ]);
    mockMmPkgApi.postDetails.and.returnValue(Promise.resolve({ code: 200, message: {} }));
    mockMmPkgApi.postUpgradePackages.and.returnValue(Promise.resolve({ code: 200, message: {} }));

    TestBed.configureTestingModule({
      declarations: [PackageDetailsViewerComponent],
      providers: [
        { provide: MagicMirrorPackageAPI, useValue: mockMmPkgApi },
        { provide: SharedStoreService,    useClass: MockSharedStoreService },
        { provide: MessageService,        useValue: jasmine.createSpyObj('MessageService', ['add']) },
      ],
      schemas: [NO_ERRORS_SCHEMA],
    });

    fixture = TestBed.createComponent(PackageDetailsViewerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('isQueued returns false when no selectedPackage', () => {
    component.selectedPackage = null;
    expect(component.isQueued).toBeFalse();
  });

  it('isQueued returns false when package not in queue', () => {
    component.selectedPackage = { ...pkg };
    component.selectedPackages = [];
    expect(component.isQueued).toBeFalse();
  });

  it('isQueued returns true when package is in queue', () => {
    component.selectedPackage = { ...pkg };
    component.selectedPackages = [{ ...pkg }];
    expect(component.isQueued).toBeTrue();
  });

  it('toggleQueue does nothing without selectedPackage', () => {
    const spy = spyOn(component.selectedPackagesChange, 'emit');
    component.selectedPackage = null;
    component.toggleQueue();
    expect(spy).not.toHaveBeenCalled();
  });

  it('toggleQueue adds package to queue when not queued', () => {
    const emitted: any[] = [];
    component.selectedPackagesChange.subscribe((v: any) => emitted.push(v));
    component.selectedPackage = { ...pkg };
    component.selectedPackages = [];
    component.toggleQueue();
    expect(emitted[0]).toEqual([pkg]);
  });

  it('toggleQueue removes package from queue when already queued', () => {
    const emitted: any[] = [];
    component.selectedPackagesChange.subscribe((v: any) => emitted.push(v));
    component.selectedPackage = { ...pkg };
    component.selectedPackages = [{ ...pkg }];
    component.toggleQueue();
    expect(emitted[0]).toEqual([]);
  });

  it('loadRemoteDetails does nothing when no selectedPackage', () => {
    component.selectedPackage = null;
    component.loadRemoteDetails();
    expect(mockMmPkgApi.postDetails).not.toHaveBeenCalled();
  });

  it('loadRemoteDetails does nothing when remote_details already present', () => {
    component.selectedPackage = { ...pkg, remote_details: { issues: 1, created: '', forks: 0 } };
    component.loadRemoteDetails();
    expect(mockMmPkgApi.postDetails).not.toHaveBeenCalled();
  });

  it('loadRemoteDetails calls postDetails and sets remote_details on success', async () => {
    const details = { issues: 3, created: '2020-01-01', forks: 2 };
    mockMmPkgApi.postDetails.and.returnValue(Promise.resolve({ code: 200, message: details }));
    component.selectedPackage = { ...pkg };
    component.loadRemoteDetails();
    expect(component.loadingRemote).toBeTrue();
    await fixture.whenStable();
    expect(component.loadingRemote).toBeFalse();
    expect(component.selectedPackage?.remote_details).toEqual(details);
  });

  it('moduleIcon returns null when no selectedPackage', () => {
    component.selectedPackage = null;
    expect(component.moduleIcon).toBeNull();
  });
});
