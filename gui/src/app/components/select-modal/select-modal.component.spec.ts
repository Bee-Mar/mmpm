import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SelectModalComponent } from './select-modal.component';

describe('SelectModalComponent', () => {
  let component: SelectModalComponent;
  let fixture: ComponentFixture<SelectModalComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SelectModalComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SelectModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
