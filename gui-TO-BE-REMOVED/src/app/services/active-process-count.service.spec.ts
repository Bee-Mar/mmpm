import { TestBed } from "@angular/core/testing";

import { ActiveProcessCountService } from "./active-process-queue.service";

describe("ActiveProcessCountService", () => {
  let service: ActiveProcessCountService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ActiveProcessCountService);
  });

  it("should be created", () => {
    expect(service).toBeTruthy();
  });
});
