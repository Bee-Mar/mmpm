import { ComponentFixture, TestBed, waitForAsync } from "@angular/core/testing";

import { AvailableUpgradesTickerComponent } from "./available-upgrades-ticker.component";

describe("AvailableUpgradesTickerComponent", () => {
  let component: AvailableUpgradesTickerComponent;
  let fixture: ComponentFixture<AvailableUpgradesTickerComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [AvailableUpgradesTickerComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AvailableUpgradesTickerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
