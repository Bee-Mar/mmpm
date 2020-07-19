import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AvailableUpgradesTickerComponent } from './available-upgrades-ticker.component';

describe('AvailableUpgradesTickerComponent', () => {
  let component: AvailableUpgradesTickerComponent;
  let fixture: ComponentFixture<AvailableUpgradesTickerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AvailableUpgradesTickerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AvailableUpgradesTickerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
