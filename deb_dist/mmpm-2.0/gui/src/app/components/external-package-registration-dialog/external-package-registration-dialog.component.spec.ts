import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { ExternalPackageRegistrationDialogComponent } from "./external-package-registration-dialog.component";

describe("ExternalPackageRegistrationDialogComponent", () => {
  let component: ExternalPackageRegistrationDialogComponent;
  let fixture: ComponentFixture<ExternalPackageRegistrationDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ExternalPackageRegistrationDialogComponent]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(
      ExternalPackageRegistrationDialogComponent
    );
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
