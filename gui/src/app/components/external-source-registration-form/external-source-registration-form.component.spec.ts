import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ExternalSourceRegistrationFormComponent } from './external-source-registration-form.component';

describe('ExternalSourceRegistrationFormComponent', () => {
  let component: ExternalSourceRegistrationFormComponent;
  let fixture: ComponentFixture<ExternalSourceRegistrationFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ExternalSourceRegistrationFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ExternalSourceRegistrationFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
