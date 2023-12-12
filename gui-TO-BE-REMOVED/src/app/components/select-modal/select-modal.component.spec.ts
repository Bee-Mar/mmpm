import { ComponentFixture, TestBed, waitForAsync } from "@angular/core/testing";

import { SelectModalComponent } from "./select-modal.component";

describe("SelectModalComponent", () => {
  let component: SelectModalComponent;
  let fixture: ComponentFixture<SelectModalComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [SelectModalComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SelectModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
