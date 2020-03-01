import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ExternalModuleSourceRegistrationComponent } from './external-module-source-registration.component';

describe('ExternalModuleSourceRegistrationComponent', () => {
  let component: ExternalModuleSourceRegistrationComponent;
  let fixture: ComponentFixture<ExternalModuleSourceRegistrationComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ExternalModuleSourceRegistrationComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ExternalModuleSourceRegistrationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
