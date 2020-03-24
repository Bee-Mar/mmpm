import { TestBed } from '@angular/core/testing';

import { TableUpdateNotifierService } from './table-update-notifier.service';

describe('TableUpdateNotifierService', () => {
  let service: TableUpdateNotifierService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TableUpdateNotifierService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
