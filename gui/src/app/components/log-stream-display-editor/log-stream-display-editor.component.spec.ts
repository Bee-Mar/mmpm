import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { LogStreamDisplayEditorComponent } from './log-stream-display-editor.component';

describe('LogStreamDisplayEditorComponent', () => {
  let component: LogStreamDisplayEditorComponent;
  let fixture: ComponentFixture<LogStreamDisplayEditorComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LogStreamDisplayEditorComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LogStreamDisplayEditorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
