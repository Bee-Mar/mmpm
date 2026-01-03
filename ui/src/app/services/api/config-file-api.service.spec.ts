import { TestBed } from "@angular/core/testing";

import { ConfigFileAPI } from "./config-file-api.service";

describe("ConfigFileAPI", () => {
  let service: ConfigFileAPI;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ConfigFileAPI);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
