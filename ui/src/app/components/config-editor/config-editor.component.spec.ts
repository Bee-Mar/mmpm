import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject, Subject } from 'rxjs';
import { MessageService } from 'primeng/api';
import { ConfigFileAPI } from '@/services/api/config-file-api.service';
import { EnvApiService } from '@/services/api/env-api.service';
import { SharedStoreService } from '@/services/shared-store.service';
import { MagicMirrorPackage } from '@/models/magicmirror-package';
import { ConfigEditorComponent } from './config-editor.component';

class MockSharedStoreService {
  packages      = new BehaviorSubject<MagicMirrorPackage[]>([]);
  configJsSaved$ = new Subject<void>();
  configJsDirty  = false;
}

describe('ConfigEditorComponent', () => {
  let component: ConfigEditorComponent;
  let fixture: ComponentFixture<ConfigEditorComponent>;

  beforeEach(() => {
    const mockConfigFileAPI = jasmine.createSpyObj('ConfigFileAPI', ['getConfigFile', 'postConfigFile']);
    mockConfigFileAPI.getConfigFile.and.returnValue(Promise.resolve(''));

    const mockEnvAPI = jasmine.createSpyObj('EnvApiService', ['get_']);
    mockEnvAPI.get_.and.returnValue(Promise.resolve({ code: 200, message: {} }));

    TestBed.configureTestingModule({
      declarations: [ConfigEditorComponent],
      providers: [
        { provide: ConfigFileAPI,    useValue: mockConfigFileAPI },
        { provide: EnvApiService,    useValue: mockEnvAPI },
        { provide: SharedStoreService, useClass: MockSharedStoreService },
        { provide: MessageService,   useValue: jasmine.createSpyObj('MessageService', ['add']) },
      ],
      schemas: [NO_ERRORS_SCHEMA],
    });
    fixture = TestBed.createComponent(ConfigEditorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
