import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { MagicMirrorAPI } from './magicmirror-api.service';

describe('MagicMirrorAPI', () => {
  let service: MagicMirrorAPI;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [MagicMirrorAPI],
    });
    service = TestBed.inject(MagicMirrorAPI);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('getStatus calls mm/status endpoint', () => {
    service.getStatus().then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('mm/status'));
    expect(req.request.method).toBe('GET');
    req.flush({ code: 200, message: [] });
  });

  it('getUpgrade calls mm/upgrade endpoint', () => {
    service.getUpgrade().then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('mm/upgrade'));
    expect(req.request.method).toBe('GET');
    req.flush({ code: 200, message: '' });
  });

  it('getInstall calls mm/install endpoint', () => {
    service.getInstall().then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('mm/install'));
    expect(req.request.method).toBe('GET');
    req.flush({ code: 200, message: '' });
  });

  it('getRemove calls mm/remove endpoint', () => {
    service.getRemove().then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('mm/remove'));
    expect(req.request.method).toBe('GET');
    req.flush({ code: 200, message: '' });
  });
});
