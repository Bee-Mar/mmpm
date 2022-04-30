import { ComponentFixture, TestBed, waitForAsync } from "@angular/core/testing";

import { MMPMLocalPackagesComponent } from "./mmpmlocal-packages.component";

describe("MMPMLocalPackagesComponent", () => {
  let component: MMPMLocalPackagesComponent;
  let fixture: ComponentFixture<MMPMLocalPackagesComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [MMPMLocalPackagesComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MMPMLocalPackagesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
