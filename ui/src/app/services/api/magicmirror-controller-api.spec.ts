import { TestBed } from "@angular/core/testing";

import { MagicMirrorAPI } from "./magicmirror-api.service";

describe("MagicMirrorAPI", () => {
  let service: MagicMirrorAPI;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MagicMirrorAPI);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
