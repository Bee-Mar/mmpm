import { ComponentFixture, TestBed } from "@angular/core/testing";

import { LogStreamViewerComponent } from "./log-stream-viewer.component";

describe("LogStreamViewerComponent", () => {
  let component: LogStreamViewerComponent;
  let fixture: ComponentFixture<LogStreamViewerComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [LogStreamViewerComponent],
    });
    fixture = TestBed.createComponent(LogStreamViewerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
