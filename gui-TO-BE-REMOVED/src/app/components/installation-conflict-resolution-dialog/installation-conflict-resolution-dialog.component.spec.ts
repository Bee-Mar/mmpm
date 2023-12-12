import { ComponentFixture, TestBed, waitForAsync } from "@angular/core/testing";

import { InstallationConflictResolutionDialogComponent } from "./installation-conflict-resolution-dialog.component";

describe("InstallationConflictResolutionDialogComponent", () => {
  let component: InstallationConflictResolutionDialogComponent;
  let fixture: ComponentFixture<InstallationConflictResolutionDialogComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [InstallationConflictResolutionDialogComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(InstallationConflictResolutionDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
