import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { MagicMirrorPackageAPI } from './magicmirror-package-api.service';

describe('MagicMirrorPackageAPI', () => {
  let service: MagicMirrorPackageAPI;
  let httpMock: HttpTestingController;

  const pkg = {
    title: 'MMM-Test',
    author: 'tester',
    repository: 'https://github.com/tester/MMM-Test',
    description: 'desc',
    directory: 'MMM-Test',
    category: 'Test',
    is_installed: false,
    is_upgradable: false,
    remote_details: null as any,
    stars: 0,
    last_updated: '2024-01-01',
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [MagicMirrorPackageAPI],
    });
    service = TestBed.inject(MagicMirrorPackageAPI);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('getPackages calls packages endpoint', () => {
    service.getPackages().then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('/api/packages'));
    expect(req.request.method).toBe('GET');
    req.flush({ code: 200, message: [] });
  });

  it('postInstallPackages calls packages/install endpoint', () => {
    service.postInstallPackages([pkg]).then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('packages/install'));
    expect(req.request.method).toBe('POST');
    req.flush({ code: 200, message: { success: [], failure: [] } });
  });

  it('postRemovePackages calls packages/remove endpoint', () => {
    service.postRemovePackages([pkg]).then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('packages/remove'));
    req.flush({ code: 200, message: { success: [], failure: [] } });
  });

  it('postUpgradePackages calls packages/upgrade endpoint', () => {
    service.postUpgradePackages([pkg]).then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('packages/upgrade'));
    expect(req.request.method).toBe('POST');
    req.flush({ code: 200, message: { success: [], failure: [] } });
  });

  it('postAddMmPkg calls packages/mm-pkg/add endpoint', () => {
    service.postAddMmPkg(pkg).then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('packages/mm-pkg/add'));
    req.flush({ code: 200, message: '' });
  });

  it('postRemoveMmPkgs calls packages/mm-pkg/remove endpoint', () => {
    service.postRemoveMmPkgs([pkg]).then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('packages/mm-pkg/remove'));
    req.flush({ code: 200, message: '' });
  });

  it('postDetails calls packages/details endpoint', () => {
    service.postDetails(pkg).then(res => expect(res.code).toBe(200));
    const req = httpMock.expectOne(r => r.url.includes('packages/details'));
    req.flush({ code: 200, message: {} });
  });
});
