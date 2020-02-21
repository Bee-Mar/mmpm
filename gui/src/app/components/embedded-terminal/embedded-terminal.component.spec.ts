import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EmbeddedTerminalComponent } from './embedded-terminal.component';

describe('EmbeddedTerminalComponent', () => {
  let component: EmbeddedTerminalComponent;
  let fixture: ComponentFixture<EmbeddedTerminalComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EmbeddedTerminalComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EmbeddedTerminalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
