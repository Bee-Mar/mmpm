import { ComponentFixture, TestBed } from "@angular/core/testing";

import { MmpmMarketPlaceComponent } from "./mmpm-marketplace.component";

describe("MmpmMarketPlaceComponent", () => {
  let component: MmpmMarketPlaceComponent;
  let fixture: ComponentFixture<MmpmMarketPlaceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [MmpmMarketPlaceComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MmpmMarketPlaceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
