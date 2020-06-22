import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { RenamePackageDirectoryDialogComponent } from "./rename-package-directory-dialog.component";

describe("RenamePackageDirectoryDialogComponent", () => {
  let component: RenamePackageDirectoryDialogComponent;
  let fixture: ComponentFixture<RenamePackageDirectoryDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RenamePackageDirectoryDialogComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RenamePackageDirectoryDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
