import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject } from 'rxjs';
import { MessageService } from 'primeng/api';
import { MagicMirrorPackageAPI } from '@/services/api/magicmirror-package-api.service';
import { SharedStoreService } from '@/services/shared-store.service';
import { CustomPackageManagerComponent } from './custom-package-manager.component';

class MockSharedStoreService {
  packages = new BehaviorSubject<any[]>([]);
}

describe('CustomPackageManagerComponent', () => {
  let component: CustomPackageManagerComponent;
  let fixture: ComponentFixture<CustomPackageManagerComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CustomPackageManagerComponent],
      providers: [
        { provide: SharedStoreService, useClass: MockSharedStoreService },
        { provide: MagicMirrorPackageAPI, useValue: jasmine.createSpyObj('MagicMirrorPackageAPI', ['install', 'remove']) },
        { provide: MessageService, useValue: jasmine.createSpyObj('MessageService', ['add']) },
      ],
      schemas: [NO_ERRORS_SCHEMA],
    });
    fixture = TestBed.createComponent(CustomPackageManagerComponent);
    component = fixture.componentInstance;
    component.loading = false;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
