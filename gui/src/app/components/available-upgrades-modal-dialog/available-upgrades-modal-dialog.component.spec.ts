import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { AvailableUpgradesModalDialogComponent } from "./available-upgrades-modal-dialog.component";

describe("AvailableUpgradesModalDialogComponent", () => {
  let component: AvailableUpgradesModalDialogComponent;
  let fixture: ComponentFixture<AvailableUpgradesModalDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [AvailableUpgradesModalDialogComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AvailableUpgradesModalDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
