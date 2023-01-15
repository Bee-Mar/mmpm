import { ComponentFixture, TestBed, waitForAsync } from "@angular/core/testing";

import { MMPMExternalPackagesComponent } from "./mmpm-external-packages.component";

describe("MMPMExternalPackagesComponent", () => {
  let component: MMPMExternalPackagesComponent;
  let fixture: ComponentFixture<MMPMExternalPackagesComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [MMPMExternalPackagesComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MMPMExternalPackagesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
