import { TestBed } from "@angular/core/testing";

import { MagicMirrorPackageAPI } from "./magicmirror-package-api.service";

describe("RestApiService", () => {
  let service: MagicMirrorPackageAPI;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MagicMirrorPackageAPI);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
