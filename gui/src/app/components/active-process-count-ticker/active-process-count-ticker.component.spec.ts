import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { ActiveProcessCountTickerComponent } from "./active-process-count-ticker.component";

describe("ActiveProcessCountTickerComponent", () => {
  let component: ActiveProcessCountTickerComponent;
  let fixture: ComponentFixture<ActiveProcessCountTickerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ActiveProcessCountTickerComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ActiveProcessCountTickerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
