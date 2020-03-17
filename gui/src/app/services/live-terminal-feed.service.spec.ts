import { TestBed } from '@angular/core/testing';

import { LiveTerminalFeedServiceService } from './live-terminal-feed-service.service';

describe('LiveTerminalFeedServiceService', () => {
  let service: LiveTerminalFeedServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LiveTerminalFeedServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
