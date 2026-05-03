import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { MagicMirrorControllerAPI } from './magicmirror-controller-api.service';

describe('MagicMirrorControllerAPI', () => {
  let service: MagicMirrorControllerAPI;
  let httpMock: HttpTestingController;

  const mmModule = { key: 'MMM-Clock', name: 'MMM-Clock' };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [MagicMirrorControllerAPI],
    });
    service = TestBed.inject(MagicMirrorControllerAPI);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('getStart calls mm-ctl/start endpoint', () => {
    service.getStart().then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('mm-ctl/start'));
    expect(req.request.method).toBe('GET');
    req.flush({ code: 200, message: '' });
  });

  it('getRestart calls mm-ctl/restart endpoint', () => {
    service.getRestart().then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('mm-ctl/restart'));
    req.flush({ code: 200, message: '' });
  });

  it('getStop calls mm-ctl/stop endpoint', () => {
    service.getStop().then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('mm-ctl/stop'));
    req.flush({ code: 200, message: '' });
  });

  it('postHide calls mm-ctl/hide endpoint', () => {
    service.postHide(mmModule as any).then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('mm-ctl/hide'));
    expect(req.request.method).toBe('POST');
    req.flush({ code: 200, message: '' });
  });

  it('postShow calls mm-ctl/show endpoint', () => {
    service.postShow(mmModule as any).then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('mm-ctl/show'));
    expect(req.request.method).toBe('POST');
    req.flush({ code: 200, message: '' });
  });
});
