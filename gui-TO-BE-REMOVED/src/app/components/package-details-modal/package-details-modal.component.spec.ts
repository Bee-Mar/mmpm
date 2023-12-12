import { ComponentFixture, TestBed, waitForAsync } from "@angular/core/testing";

import { PackageDetailsModalComponent } from "./package-details-modal.component";

describe("PackageDetailsModalComponent", () => {
  let component: PackageDetailsModalComponent;
  let fixture: ComponentFixture<PackageDetailsModalComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [PackageDetailsModalComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PackageDetailsModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
