import { TestBed, fakeAsync, tick } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { SharedStoreService } from './shared-store.service';

describe('SharedStoreService', () => {
  let service: SharedStoreService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [SharedStoreService],
    });
    service = TestBed.inject(SharedStoreService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('configJsDirty defaults to false', () => {
    expect(service.configJsDirty).toBeFalse();
  });

  it('notifyConfigJsSaved sets configJsDirty to true and emits', () => {
    let emitted = false;
    service.configJsSaved$.subscribe(() => (emitted = true));
    service.notifyConfigJsSaved();
    expect(service.configJsDirty).toBeTrue();
    expect(emitted).toBeTrue();
  });

  it('packages observable emits empty array by default', (done) => {
    service.packages.subscribe(pkgs => {
      expect(pkgs).toEqual([]);
      done();
    });
  });

  it('load triggers HTTP requests and updates packages on success', fakeAsync(() => {
    const mockPackages = [
      {
        title: 'MMM-Test', author: 'a', repository: 'r', description: 'd',
        directory: 'MMM-Test', category: 'Test', is_installed: false,
        is_upgradable: false, remote_details: null as any, stars: 0, last_updated: '',
      },
    ];

    const received: any[] = [];
    service.packages.subscribe(pkgs => received.push(pkgs));

    service.load();

    const envReq = httpMock.expectOne(r => r.url.includes('/api/env'));
    envReq.flush({ code: 200, message: {} });

    const pkgReq = httpMock.expectOne(r => r.url.endsWith('/api/packages'));
    pkgReq.flush({ code: 200, message: mockPackages });

    tick();

    const dbReq = httpMock.expectOne(r => r.url.includes('db/info'));
    dbReq.flush({ code: 200, message: { last_update: '2024-01-01', categories: 1, packages: 1 } });

    const upgradeReq = httpMock.expectOne(r => r.url.includes('db/upgradable'));
    upgradeReq.flush({ code: 200, message: { mmpm: false, MagicMirror: false, packages: [] } });

    tick();

    expect(received.length).toBeGreaterThan(0);
    expect(received[received.length - 1]).toEqual(mockPackages);
  }));
});
