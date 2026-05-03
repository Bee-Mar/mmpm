import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject } from 'rxjs';
import { SharedStoreService } from '@/services/shared-store.service';
import { MarketPlaceComponent } from './marketplace.component';

class MockSharedStoreService {
  packages = new BehaviorSubject<any[]>([]);
}

describe('MarketPlaceComponent', () => {
  let component: MarketPlaceComponent;
  let fixture: ComponentFixture<MarketPlaceComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MarketPlaceComponent],
      providers: [
        { provide: SharedStoreService, useClass: MockSharedStoreService },
      ],
      schemas: [NO_ERRORS_SCHEMA],
    });
    fixture = TestBed.createComponent(MarketPlaceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
