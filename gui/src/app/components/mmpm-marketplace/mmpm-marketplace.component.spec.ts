import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MMPMMarketplaceComponent } from './mmpmmarketplace.component';

describe('MMPMMarketplaceComponent', () => {
  let component: MMPMMarketplaceComponent;
  let fixture: ComponentFixture<MMPMMarketplaceComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MMPMMarketplaceComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MMPMMarketplaceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
