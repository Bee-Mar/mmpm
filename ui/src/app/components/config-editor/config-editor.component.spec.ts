import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfigEditorComponent } from './config-editor.component';

describe('ConfigEditorComponent', () => {
  let component: ConfigEditorComponent;
  let fixture: ComponentFixture<ConfigEditorComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ConfigEditorComponent]
    });
    fixture = TestBed.createComponent(ConfigEditorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
