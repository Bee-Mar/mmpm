import { ComponentFixture, TestBed, waitForAsync } from "@angular/core/testing";

import { MMPMMarketplaceComponent } from "./mmpmmarketplace.component";

describe("MMPMMarketplaceComponent", () => {
  let component: MMPMMarketplaceComponent;
  let fixture: ComponentFixture<MMPMMarketplaceComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [MMPMMarketplaceComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MMPMMarketplaceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
