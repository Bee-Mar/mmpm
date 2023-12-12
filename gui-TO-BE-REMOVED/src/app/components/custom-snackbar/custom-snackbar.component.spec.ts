import { ComponentFixture, TestBed, waitForAsync } from "@angular/core/testing";

import { CustomSnackbarComponent } from "./custom-snackbar.component";

describe("CustomSnackbarComponent", () => {
  let component: CustomSnackbarComponent;
  let fixture: ComponentFixture<CustomSnackbarComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [CustomSnackbarComponent],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CustomSnackbarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
