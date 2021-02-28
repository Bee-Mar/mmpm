import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { ActiveProcessesModalComponent } from "./active-processes-modal.component";

describe("ActiveProcessesModalComponent", () => {
  let component: ActiveProcessesModalComponent;
  let fixture: ComponentFixture<ActiveProcessesModalComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ActiveProcessesModalComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ActiveProcessesModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
