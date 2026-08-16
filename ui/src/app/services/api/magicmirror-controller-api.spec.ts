import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { MagicMirrorControllerAPI } from './magicmirror-controller-api.service';
import { MagicMirrorModule } from '@/models/magicmirror-module';

describe('MagicMirrorControllerAPI', () => {
  let service: MagicMirrorControllerAPI;
  let httpMock: HttpTestingController;

  const mmModule: MagicMirrorModule = { key: 1, name: 'MMM-Clock', hidden: false };

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

  it('getStart calls mm/start endpoint', () => {
    service.getStart().then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('mm/start'));
    expect(req.request.method).toBe('GET');
    req.flush({ code: 200, message: '' });
  });

  it('getRestart calls mm/restart endpoint', () => {
    service.getRestart().then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('mm/restart'));
    expect(req.request.method).toBe('GET');
    req.flush({ code: 200, message: '' });
  });

  it('getStop calls mm/stop endpoint', () => {
    service.getStop().then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('mm/stop'));
    expect(req.request.method).toBe('GET');
    req.flush({ code: 200, message: '' });
  });

  it('postHide calls mm/hide endpoint', () => {
    service.postHide(mmModule).then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('mm/hide'));
    expect(req.request.method).toBe('POST');
    req.flush({ code: 200, message: '' });
  });

  it('postShow calls mm/show endpoint', () => {
    service.postShow(mmModule).then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('mm/show'));
    expect(req.request.method).toBe('POST');
    req.flush({ code: 200, message: '' });
  });
});
