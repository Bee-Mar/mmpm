import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MagicMirrorControllerComponent } from './magicmirror-controller.component';

describe('MagicMirrorControllerComponent', () => {
  let component: MagicMirrorControllerComponent;
  let fixture: ComponentFixture<MagicMirrorControllerComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MagicMirrorControllerComponent],
      schemas: [NO_ERRORS_SCHEMA],
    });
    fixture = TestBed.createComponent(MagicMirrorControllerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
