import { ComponentFixture, TestBed } from "@angular/core/testing";

import { MagicMirrorControllerComponent } from "./magic-mirror-controller.component";

describe("MagicMirrorControllerComponent", () => {
  let component: MagicMirrorControllerComponent;
  let fixture: ComponentFixture<MagicMirrorControllerComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MagicMirrorControllerComponent],
    });
    fixture = TestBed.createComponent(MagicMirrorControllerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
