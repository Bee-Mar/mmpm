import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MagicMirrorDatabaseComponent } from './magic-mirror-database.component';

describe('MagicMirrorDatabaseComponent', () => {
  let component: MagicMirrorDatabaseComponent;
  let fixture: ComponentFixture<MagicMirrorDatabaseComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MagicMirrorDatabaseComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MagicMirrorDatabaseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
