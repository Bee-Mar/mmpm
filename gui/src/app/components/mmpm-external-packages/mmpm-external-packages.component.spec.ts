import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { MMPMExternalPackagesComponent } from "./mmpm-external-packages.component";

describe("MMPMExternalPackagesComponent", () => {
  let component: MMPMExternalPackagesComponent;
  let fixture: ComponentFixture<MMPMExternalPackagesComponent>;

  beforeEach(async(() => {
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
