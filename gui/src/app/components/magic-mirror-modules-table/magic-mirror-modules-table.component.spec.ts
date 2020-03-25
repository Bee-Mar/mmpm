import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { MagicMirrorModulesTableComponent } from "./magic-mirror-modules-table.component";

describe("MagicMirrorModulesTableComponent", () => {
  let component: MagicMirrorModulesTableComponent;
  let fixture: ComponentFixture<MagicMirrorModulesTableComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [MagicMirrorModulesTableComponent]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MagicMirrorModulesTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
