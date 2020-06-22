import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MmpmTableContainerComponent } from './mmpm-table-container.component';

describe('MmpmTableContainerComponent', () => {
  let component: MmpmTableContainerComponent;
  let fixture: ComponentFixture<MmpmTableContainerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MmpmTableContainerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MmpmTableContainerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
