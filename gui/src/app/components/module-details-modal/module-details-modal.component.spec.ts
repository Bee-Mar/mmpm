import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ModuleDetailsModalComponent } from './module-details-modal.component';

describe('ModuleDetailsModalComponent', () => {
  let component: ModuleDetailsModalComponent;
  let fixture: ComponentFixture<ModuleDetailsModalComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ModuleDetailsModalComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ModuleDetailsModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
