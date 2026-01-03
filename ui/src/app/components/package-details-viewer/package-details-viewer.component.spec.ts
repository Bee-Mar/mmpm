import { ComponentFixture, TestBed } from "@angular/core/testing";

import { PackageDetailsViewerComponent } from "./package-details-viewer.component";

describe("PackageDetailsViewerComponent", () => {
  let component: PackageDetailsViewerComponent;
  let fixture: ComponentFixture<PackageDetailsViewerComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [PackageDetailsViewerComponent],
    });
    fixture = TestBed.createComponent(PackageDetailsViewerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
