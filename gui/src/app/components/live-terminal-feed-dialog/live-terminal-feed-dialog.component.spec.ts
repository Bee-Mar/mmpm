import { async, ComponentFixture, TestBed } from "@angular/core/testing";
import { LiveTerminalFeedDialogComponent } from "./live-terminal-feed-dialog.component";

describe("LiveTerminalFeedDialogComponent", () => {
  let component: LiveTerminalFeedDialogComponent;
  let fixture: ComponentFixture<LiveTerminalFeedDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [LiveTerminalFeedDialogComponent]
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LiveTerminalFeedDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
