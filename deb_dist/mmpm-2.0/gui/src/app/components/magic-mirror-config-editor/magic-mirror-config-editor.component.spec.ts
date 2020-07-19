import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { MagicMirrorConfigEditorComponent } from "./magic-mirror-config-editor.component";

describe("MagicMirrorConfigEditorComponent", () => {
  let component: MagicMirrorConfigEditorComponent;
  let fixture: ComponentFixture<MagicMirrorConfigEditorComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [MagicMirrorConfigEditorComponent]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MagicMirrorConfigEditorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
