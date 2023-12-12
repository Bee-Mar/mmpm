import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CustomPackageManagerComponent } from './custom-package-manager.component';

describe('CustomPackageManagerComponent', () => {
  let component: CustomPackageManagerComponent;
  let fixture: ComponentFixture<CustomPackageManagerComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CustomPackageManagerComponent]
    });
    fixture = TestBed.createComponent(CustomPackageManagerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
