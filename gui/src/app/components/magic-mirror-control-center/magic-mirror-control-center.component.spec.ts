import { ComponentFixture, TestBed, waitForAsync } from "@angular/core/testing";

import { MagicMirrorControlCenterComponent } from "./magic-mirror-control-center.component";

describe("MagicMirrorControlCenterComponent", () => {
  let component: MagicMirrorControlCenterComponent;
  let fixture: ComponentFixture<MagicMirrorControlCenterComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [MagicMirrorControlCenterComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MagicMirrorControlCenterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
