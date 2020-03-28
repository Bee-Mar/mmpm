import { TestBed } from '@angular/core/testing';

import { RemoteControlEnablerService } from './remote-control-enabler.service';

describe('RemoteControlEnablerService', () => {
  let service: RemoteControlEnablerService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RemoteControlEnablerService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
