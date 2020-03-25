import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { ExternalSourceRegistrationDialogComponent } from "./external-source-registration-form.component";

describe("ExternalSourceRegistrationDialogComponent", () => {
  let component: ExternalSourceRegistrationDialogComponent;
  let fixture: ComponentFixture<ExternalSourceRegistrationDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ExternalSourceRegistrationDialogComponent]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(
      ExternalSourceRegistrationDialogComponent
    );
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
