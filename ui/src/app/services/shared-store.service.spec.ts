import { TestBed } from "@angular/core/testing";

import { SharedStoreService } from "./shared-store.service";

describe("SharedStoreService", () => {
  let service: SharedStoreService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SharedStoreService);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
