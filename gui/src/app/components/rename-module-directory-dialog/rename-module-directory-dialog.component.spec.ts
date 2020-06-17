import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RenameModuleDirectoryDialogComponent } from './rename-module-directory-dialog.component';

describe('RenameModuleDirectoryDialogComponent', () => {
  let component: RenameModuleDirectoryDialogComponent;
  let fixture: ComponentFixture<RenameModuleDirectoryDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RenameModuleDirectoryDialogComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RenameModuleDirectoryDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
