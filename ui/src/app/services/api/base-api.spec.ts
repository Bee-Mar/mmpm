import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { BaseAPI } from './base-api';

describe('BaseAPI', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
    });
  });

  it('should create an instance', () => {
    const service = TestBed.inject(BaseAPI);
    expect(service).toBeTruthy();
  });
});
