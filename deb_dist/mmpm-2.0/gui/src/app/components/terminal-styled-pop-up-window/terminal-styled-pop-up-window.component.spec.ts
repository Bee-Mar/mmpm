import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { TerminalStyledPopUpWindowComponent } from './terminal-styled-pop-up-window.component';

describe('TerminalStyledPopUpWindowComponent', () => {
  let component: TerminalStyledPopUpWindowComponent;
  let fixture: ComponentFixture<TerminalStyledPopUpWindowComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ TerminalStyledPopUpWindowComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(TerminalStyledPopUpWindowComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
