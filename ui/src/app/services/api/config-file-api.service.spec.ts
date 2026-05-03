import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ConfigFileAPI } from './config-file-api.service';

describe('ConfigFileAPI', () => {
  let service: ConfigFileAPI;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ConfigFileAPI],
    });
    service = TestBed.inject(ConfigFileAPI);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('getConfigFile calls configs/retrieve endpoint', () => {
    service.getConfigFile('config.js').then(content => expect(content).toBe('module.exports = {}'));
    const req = httpMock.expectOne(r => r.url.includes('configs/retrieve/config.js'));
    expect(req.request.method).toBe('GET');
    req.flush('module.exports = {}');
  });

  it('postConfigFile calls configs/update endpoint', () => {
    service.postConfigFile('config.js', 'module.exports = {}').then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('configs/update/config.js'));
    expect(req.request.method).toBe('POST');
    expect(req.request.body.contents).toBe('module.exports = {}');
    req.flush({ code: 200, message: 'ok' });
  });
});
