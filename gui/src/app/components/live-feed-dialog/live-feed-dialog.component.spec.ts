import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { LiveFeedDialogComponent } from './live-feed-dialog.component';

describe('LiveFeedDialogComponent', () => {
  let component: LiveFeedDialogComponent;
  let fixture: ComponentFixture<LiveFeedDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LiveFeedDialogComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LiveFeedDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
