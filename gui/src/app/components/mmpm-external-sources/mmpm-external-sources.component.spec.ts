import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MMPMExternalSourcesComponent } from './mmpmexternal-sources.component';

describe('MMPMExternalSourcesComponent', () => {
  let component: MMPMExternalSourcesComponent;
  let fixture: ComponentFixture<MMPMExternalSourcesComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MMPMExternalSourcesComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MMPMExternalSourcesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
