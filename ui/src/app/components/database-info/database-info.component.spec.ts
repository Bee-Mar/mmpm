import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
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
}

describe('DatabaseInfoComponent', () => {
  let component: DatabaseInfoComponent;
  let fixture: ComponentFixture<DatabaseInfoComponent>;

  beforeEach(() => {
    const mockBaseAPI = jasmine.createSpyObj('BaseAPI', ['get_', 'route', 'headers']);
    mockBaseAPI.get_.and.returnValue(Promise.resolve({ code: 200, message: '' }));

    TestBed.configureTestingModule({
      declarations: [DatabaseInfoComponent],
      providers: [
        { provide: BaseAPI,              useValue: mockBaseAPI },
        { provide: MagicMirrorPackageAPI, useValue: jasmine.createSpyObj('MagicMirrorPackageAPI', ['get_', 'getPackages']) },
        { provide: MagicMirrorAPI,       useValue: jasmine.createSpyObj('MagicMirrorAPI', ['getStatus']) },
        { provide: SharedStoreService,   useClass: MockSharedStoreService },
        { provide: MessageService,       useValue: jasmine.createSpyObj('MessageService', ['add']) },
        { provide: ConfirmationService,  useValue: jasmine.createSpyObj('ConfirmationService', ['confirm']) },
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
});
