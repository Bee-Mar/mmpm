import { async, ComponentFixture, TestBed } from "@angular/core/testing";

import { MMPMTableContainerComponent } from "./mmpm-table-container.component";

describe("MMPMTableContainerComponent", () => {
  let component: MMPMTableContainerComponent;
  let fixture: ComponentFixture<MMPMTableContainerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MMPMTableContainerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MMPMTableContainerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
