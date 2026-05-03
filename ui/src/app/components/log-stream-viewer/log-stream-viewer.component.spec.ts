import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { removeCookie } from 'typescript-cookie';
import { BaseAPI } from '@/services/api/base-api';
import { LogStreamViewerComponent } from './log-stream-viewer.component';

const mockBaseAPI = jasmine.createSpyObj('BaseAPI', ['get_', 'getZipArchive', 'route', 'headers']);
mockBaseAPI.getZipArchive.and.returnValue(Promise.resolve(new ArrayBuffer(0)));

/** Cookie names written by the component */
const LEVEL_COOKIE = 'mmpm-log-level-filter';
const AGE_COOKIE = 'mmpm-log-max-age-h';
const FONT_COOKIE = 'mmpm-log-stream-font-size';

function clearComponentCookies() {
  [LEVEL_COOKIE, AGE_COOKIE, FONT_COOKIE].forEach(name => {
    // Remove with both path variants used by typescript-cookie
    removeCookie(name, { path: '/' });
    removeCookie(name, { path: '' });
  });
}

describe('LogStreamViewerComponent', () => {
  let component: LogStreamViewerComponent;
  let fixture: ComponentFixture<LogStreamViewerComponent>;

  beforeEach(() => {
    // Wipe cookies so every test starts from a known default state
    clearComponentCookies();

    TestBed.configureTestingModule({
      declarations: [LogStreamViewerComponent],
      providers: [{ provide: BaseAPI, useValue: mockBaseAPI }],
      schemas: [NO_ERRORS_SCHEMA],
    });

    fixture = TestBed.createComponent(LogStreamViewerComponent);
    component = fixture.componentInstance;
    // Do not call detectChanges here — avoids socket.io connection attempts.
    // Logic methods under test do not require ngOnInit to have run.
  });

  afterEach(() => {
    component.ngOnDestroy();
    clearComponentCookies();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  // ── defaults ──────────────────────────────────────────────────────────────

  it('has all five log levels active by default', () => {
    expect(component.activeLevels.size).toBe(5);
    (['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] as const).forEach(level => {
      expect(component.activeLevels.has(level)).toBeTrue();
    });
  });

  it('defaults maxAgeHours to 6', () => {
    expect(component.maxAgeHours).toBe(6);
  });

  it('starts with following=true', () => {
    expect(component.following).toBeTrue();
  });

  // ── toggleLevel ───────────────────────────────────────────────────────────

  describe('toggleLevel', () => {
    it('removes an active level', () => {
      component.toggleLevel('DEBUG');
      expect(component.activeLevels.has('DEBUG')).toBeFalse();
    });

    it('adds an inactive level', () => {
      component.activeLevels = new Set(['INFO', 'WARNING', 'ERROR', 'CRITICAL']);
      component.toggleLevel('DEBUG');
      expect(component.activeLevels.has('DEBUG')).toBeTrue();
    });

    it('does not mutate the original set', () => {
      const original = component.activeLevels;
      component.toggleLevel('DEBUG');
      expect(component.activeLevels).not.toBe(original);
    });

    it('re-enables a level in displayed logs', () => {
      const entry = { raw: 'debug line', level: 'DEBUG' as const, timestamp: new Date() };
      (component as any).allLogs = [entry];
      component.activeLevels = new Set(['INFO', 'WARNING', 'ERROR', 'CRITICAL']);

      component.toggleLevel('DEBUG');
      expect(component.logs).toContain('debug line');
    });

    it('hides a deactivated level from displayed logs', () => {
      const entry = { raw: 'debug line', level: 'DEBUG' as const, timestamp: new Date() };
      (component as any).allLogs = [entry];

      component.toggleLevel('DEBUG');
      expect(component.logs).not.toContain('debug line');
    });
  });

  // ── setMaxAge ─────────────────────────────────────────────────────────────

  describe('setMaxAge', () => {
    it('updates maxAgeHours', () => {
      component.setMaxAge(12);
      expect(component.maxAgeHours).toBe(12);
    });

    it('prunes entries older than the new window', () => {
      const twoHoursAgo = new Date(Date.now() - 2 * 3600 * 1000 - 1);
      (component as any).allLogs = [
        { raw: 'old', level: 'INFO', timestamp: twoHoursAgo },
        { raw: 'new', level: 'INFO', timestamp: new Date() },
      ];

      component.setMaxAge(1);
      expect((component as any).allLogs.length).toBe(1);
      expect((component as any).allLogs[0].raw).toBe('new');
    });

    it('keeps entries within the new window', () => {
      const thirtyMinAgo = new Date(Date.now() - 30 * 60 * 1000);
      (component as any).allLogs = [{ raw: 'recent', level: 'INFO', timestamp: thirtyMinAgo }];

      component.setMaxAge(1);
      expect((component as any).allLogs.length).toBe(1);
    });
  });

  // ── scrollToBottom ────────────────────────────────────────────────────────

  describe('scrollToBottom', () => {
    it('is a no-op when the Monaco editor is not initialised', () => {
      expect(() => component.scrollToBottom()).not.toThrow();
    });

    it('sets following to true', () => {
      component.following = false;
      const mockEditor = {
        setScrollPosition: jasmine.createSpy(),
        getScrollHeight: jasmine.createSpy().and.returnValue(500),
      };
      (component as any).monacoEditor = mockEditor;
      component.scrollToBottom();
      expect(component.following).toBeTrue();
    });

    it('scrolls the editor to the bottom', () => {
      const mockEditor = {
        setScrollPosition: jasmine.createSpy(),
        getScrollHeight: jasmine.createSpy().and.returnValue(800),
      };
      (component as any).monacoEditor = mockEditor;
      component.scrollToBottom();
      expect(mockEditor.setScrollPosition).toHaveBeenCalledWith({ scrollTop: 800 });
    });
  });

  // ── onEditorInit ──────────────────────────────────────────────────────────

  describe('onEditorInit', () => {
    let contentChangeCallback: () => void;
    let scrollChangeCallback: () => void;
    let mockEditor: any;

    beforeEach(() => {
      mockEditor = {
        setScrollPosition: jasmine.createSpy(),
        getScrollHeight: jasmine.createSpy().and.returnValue(400),
        getScrollTop: jasmine.createSpy().and.returnValue(380),
        getLayoutInfo: jasmine.createSpy().and.returnValue({ height: 200 }),
        onDidChangeModelContent: jasmine.createSpy().and.callFake((cb: () => void) => {
          contentChangeCallback = cb;
        }),
        onDidScrollChange: jasmine.createSpy().and.callFake((cb: () => void) => {
          scrollChangeCallback = cb;
        }),
      };
    });

    it('stores the editor reference', () => {
      component.onEditorInit(mockEditor);
      expect((component as any).monacoEditor).toBe(mockEditor);
    });

    it('registers a content-change listener', () => {
      component.onEditorInit(mockEditor);
      expect(mockEditor.onDidChangeModelContent).toHaveBeenCalled();
    });

    it('registers a scroll-change listener', () => {
      component.onEditorInit(mockEditor);
      expect(mockEditor.onDidScrollChange).toHaveBeenCalled();
    });

    it('scrolls to bottom on content change when following', () => {
      component.following = true;
      component.onEditorInit(mockEditor);
      contentChangeCallback();
      expect(mockEditor.setScrollPosition).toHaveBeenCalledWith({ scrollTop: 400 });
    });

    it('does not scroll on content change when not following', () => {
      component.following = false;
      component.onEditorInit(mockEditor);
      contentChangeCallback();
      expect(mockEditor.setScrollPosition).not.toHaveBeenCalled();
    });

    it('sets following=false when scrolled away from bottom', () => {
      // scrollTop(100) + height(200) = 300 < scrollHeight(400) - 20 = 380 → not at bottom
      mockEditor.getScrollTop.and.returnValue(100);
      mockEditor.getScrollHeight.and.returnValue(400);
      mockEditor.getLayoutInfo.and.returnValue({ height: 200 });
      component.following = true;
      component.onEditorInit(mockEditor);
      fixture.ngZone!.run(() => scrollChangeCallback());
      expect(component.following).toBeFalse();
    });

    it('sets following=true when at bottom', () => {
      // scrollTop(200) + height(200) = 400 >= scrollHeight(400) - 20 = 380 → at bottom
      mockEditor.getScrollTop.and.returnValue(200);
      mockEditor.getScrollHeight.and.returnValue(400);
      mockEditor.getLayoutInfo.and.returnValue({ height: 200 });
      component.following = false;
      component.onEditorInit(mockEditor);
      fixture.ngZone!.run(() => scrollChangeCallback());
      expect(component.following).toBeTrue();
    });
  });

  // ── parseEntry (private) ──────────────────────────────────────────────────

  describe('parseEntry', () => {
    function parse(raw: string) {
      return (component as any).parseEntry(raw) as { raw: string; level: string; timestamp: Date };
    }

    it('preserves the raw string', () => {
      const raw = '{"level":"INFO","timestamp":"2024-01-15 10:30:45,000"}';
      expect(parse(raw).raw).toBe(raw);
    });

    it('extracts the log level from JSON', () => {
      expect(parse('{"level":"WARNING","timestamp":"2024-01-15 10:00:00,000"}').level).toBe('WARNING');
    });

    it('extracts all valid log levels', () => {
      (['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] as const).forEach(level => {
        expect(parse(`{"level":"${level}","timestamp":"2024-01-15 10:00:00,000"}`).level).toBe(level);
      });
    });

    it('defaults to INFO for non-JSON input', () => {
      expect(parse('plain text log line').level).toBe('INFO');
    });

    it('defaults to INFO for unknown log level', () => {
      expect(parse('{"level":"VERBOSE","timestamp":"2024-01-15 10:00:00,000"}').level).toBe('INFO');
    });

    it('parses timestamp from JSON', () => {
      const entry = parse('{"level":"INFO","timestamp":"2024-01-15 10:30:45,123"}');
      expect(entry.timestamp).toBeInstanceOf(Date);
      expect(isNaN(entry.timestamp.getTime())).toBeFalse();
    });

    it('falls back to current time for an invalid timestamp', () => {
      const before = Date.now();
      const entry = parse('{"level":"INFO","timestamp":"not-a-date"}');
      expect(entry.timestamp.getTime()).toBeGreaterThanOrEqual(before);
    });
  });

  // ── recomputeLogs (private) ───────────────────────────────────────────────

  describe('recomputeLogs', () => {
    it('includes entries matching active levels', () => {
      (component as any).allLogs = [
        { raw: 'info line', level: 'INFO', timestamp: new Date() },
        { raw: 'debug line', level: 'DEBUG', timestamp: new Date() },
      ];
      component.activeLevels = new Set(['INFO']);
      (component as any).recomputeLogs();
      expect(component.logs).toContain('info line');
      expect(component.logs).not.toContain('debug line');
    });

    it('joins entries with double newlines', () => {
      (component as any).allLogs = [
        { raw: 'a', level: 'INFO', timestamp: new Date() },
        { raw: 'b', level: 'INFO', timestamp: new Date() },
      ];
      component.activeLevels = new Set(['INFO']);
      (component as any).recomputeLogs();
      expect(component.logs).toBe('a\n\nb');
    });

    it('produces empty string when all levels are deactivated', () => {
      (component as any).allLogs = [
        { raw: 'info line', level: 'INFO', timestamp: new Date() },
      ];
      component.activeLevels = new Set<any>([]);
      (component as any).recomputeLogs();
      expect(component.logs).toBe('');
    });
  });

  // ── pruneOldLogs (private) ────────────────────────────────────────────────

  describe('pruneOldLogs', () => {
    it('removes entries older than maxAgeHours', () => {
      component.maxAgeHours = 1;
      const old = new Date(Date.now() - 2 * 3600 * 1000);
      (component as any).allLogs = [
        { raw: 'old', level: 'INFO', timestamp: old },
        { raw: 'new', level: 'INFO', timestamp: new Date() },
      ];
      (component as any).pruneOldLogs();
      expect((component as any).allLogs.length).toBe(1);
      expect((component as any).allLogs[0].raw).toBe('new');
    });

    it('keeps all entries when all are within the window', () => {
      component.maxAgeHours = 24;
      (component as any).allLogs = [
        { raw: 'a', level: 'INFO', timestamp: new Date(Date.now() - 60_000) },
        { raw: 'b', level: 'INFO', timestamp: new Date() },
      ];
      (component as any).pruneOldLogs();
      expect((component as any).allLogs.length).toBe(2);
    });

    it('triggers recomputeLogs when entries are removed', () => {
      component.maxAgeHours = 1;
      const old = new Date(Date.now() - 2 * 3600 * 1000);
      (component as any).allLogs = [{ raw: 'old', level: 'INFO', timestamp: old }];
      component.activeLevels = new Set(['INFO'] as const);
      component.logs = 'old';

      fixture.ngZone!.run(() => (component as any).pruneOldLogs());
      expect(component.logs).toBe('');
    });
  });

  // ── ngOnDestroy ───────────────────────────────────────────────────────────

  describe('ngOnDestroy', () => {
    it('clears the prune interval', () => {
      const clearSpy = spyOn(window, 'clearInterval').and.callThrough();
      (component as any).pruneTimer = setInterval(() => {}, 999_999);
      component.ngOnDestroy();
      expect(clearSpy).toHaveBeenCalled();
    });

    it('disconnects a connected socket', () => {
      const mockSocket = { connected: true, disconnect: jasmine.createSpy('disconnect') };
      component.socket = mockSocket as any;
      component.ngOnDestroy();
      expect(mockSocket.disconnect).toHaveBeenCalled();
    });

    it('does not call disconnect when socket is not connected', () => {
      const mockSocket = { connected: false, disconnect: jasmine.createSpy('disconnect') };
      component.socket = mockSocket as any;
      component.ngOnDestroy();
      expect(mockSocket.disconnect).not.toHaveBeenCalled();
    });
  });
});
