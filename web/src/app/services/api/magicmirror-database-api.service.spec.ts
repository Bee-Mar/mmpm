import { TestBed } from '@angular/core/testing';

import { MagicMirrorDatabaseAPI } from './magicmirror-database-api.service';

describe('MagicMirrorDatabaseAPIService', () => {
  let service: MagicMirrorDatabaseAPI;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MagicMirrorDatabaseAPI);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
