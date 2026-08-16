import {
  Component,
  HostListener,
  NgZone,
  OnDestroy,
  OnInit,
  ViewChild,
  inject,
} from '@angular/core';
import { io, Socket } from 'socket.io-client';
import { getCookie, setCookie } from '@/utils/utils';
import { BaseAPI } from '@/services/api/base-api';
import { EditorComponent } from 'ngx-monaco-editor-v2';

type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';

interface LogEntry {
  raw: string;
  level: LogLevel;
  timestamp: Date;
}

const ALL_LEVELS: LogLevel[] = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'];
const MAX_AGE_OPTIONS = [1, 2, 4, 6, 12, 24] as const;
const DEFAULT_MAX_AGE_H = 6;
const PRUNE_INTERVAL_MS = 2 * 60 * 1000; // check every 2 minutes

@Component({
  selector: 'app-log-stream-viewer',
  templateUrl: './log-stream-viewer.component.html',
  styleUrls: ['./log-stream-viewer.component.scss'],
  standalone: false,
})
export class LogStreamViewerComponent implements OnInit, OnDestroy {
  private base_api = inject(BaseAPI);
  private zone = inject(NgZone);

  @ViewChild(EditorComponent, { static: false })
  public editor: EditorComponent;

  public socket: Socket | undefined;
  public logs = '';
  public following = true;
  public fontSize = Number(getCookie('mmpm-log-stream-font-size', '12'));
  public readonly ALL_LEVELS = ALL_LEVELS;
  public readonly MAX_AGE_OPTIONS = MAX_AGE_OPTIONS;
  public activeLevels = new Set<LogLevel>(this.loadLevelCookie());
  public maxAgeHours: number = this.loadMaxAgeCookie();

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private monacoEditor: any = null;
  private allLogs: LogEntry[] = [];
  private pruneTimer: ReturnType<typeof setInterval> | null = null;

  public options = {
    language: 'text',
    readOnly: true,
    theme: 'vs-dark',
    scrollBeyondLastLine: false,
    fontSize: this.fontSize,
    minimap: { enabled: false },
    scrollbar: {
      useShadows: true,
      verticalHasArrows: false,
      horizontalHasArrows: false,
      vertical: 'visible' as const,
      verticalScrollbarSize: 12,
      horizontalScrollbarSize: 12,
      arrowSize: 30,
    },
    automaticLayout: true,
  };

  public ngOnInit(): void {
    this.fontSize = Number(getCookie('mmpm-log-stream-font-size', '12'));

    this.socket = io(`ws://${window.location.hostname}:6789`, { reconnection: true });

    this.socket.on('connect', () => {
      console.log('Connected to Socket.IO log server');
    });

    this.socket.on('connect_error', () => {
      console.log('Failed to connect to MMPM Log Server');
    });

    this.socket.on('logs', (data: string) => {
      const entry = this.parseEntry(data);
      this.allLogs.push(entry);
      if (this.activeLevels.has(entry.level)) {
        this.logs += entry.raw + '\n\n';
        // scrolling is handled by onDidChangeModelContent once Monaco updates
      }
    });

    this.pruneTimer = setInterval(() => this.pruneOldLogs(), PRUNE_INTERVAL_MS);
  }

  public ngOnDestroy(): void {
    if (this.socket?.connected) this.socket.disconnect();
    if (this.pruneTimer) clearInterval(this.pruneTimer);
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  public onEditorInit(editor: any): void {
    this.monacoEditor = editor;

    // Fires after Monaco's model is already updated — safe to read true scrollHeight
    editor.onDidChangeModelContent(() => {
      if (this.following) {
        editor.setScrollPosition({ scrollTop: editor.getScrollHeight() });
      }
    });

    editor.onDidScrollChange(() => {
      const scrollTop: number = editor.getScrollTop();
      const scrollHeight: number = editor.getScrollHeight();
      const height: number = editor.getLayoutInfo().height;
      const atBottom = scrollTop + height >= scrollHeight - 20;
      this.zone.run(() => { this.following = atBottom; });
    });
  }

  public scrollToBottom(): void {
    if (!this.monacoEditor) return;
    this.following = true;
    this.monacoEditor.setScrollPosition({ scrollTop: this.monacoEditor.getScrollHeight() });
  }

  public toggleLevel(level: LogLevel): void {
    const next = new Set(this.activeLevels);
    if (next.has(level)) {
      next.delete(level);
    } else {
      next.add(level);
    }
    this.activeLevels = next;
    setCookie('mmpm-log-level-filter', [...next].join(','));
    this.recomputeLogs();
  }

  public onFontSizeChange(): void {
    setCookie('mmpm-log-stream-font-size', String(this.fontSize));
    this.options = Object.assign({}, this.options, { fontSize: this.fontSize });
  }

  public onDownload(): void {
    this.base_api.getZipArchive('logs/archive').then((archive: ArrayBuffer) => {
      const blob = new Blob([archive], { type: 'application/zip' });
      const date = new Date();
      const file_name = `mmpm-logs-${date.getFullYear()}-${date.getMonth()}-${date.getDay()}.zip`;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a') as HTMLAnchorElement;
      a.href = url;
      a.download = file_name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  @HostListener('window:beforeunload')
  public beforeUnload(): void {
    this.socket?.close();
  }

  private loadLevelCookie(): LogLevel[] {
    const saved = getCookie('mmpm-log-level-filter', ALL_LEVELS.join(','));
    const parsed = saved.split(',').filter((v): v is LogLevel => (ALL_LEVELS as string[]).includes(v));
    return parsed.length ? parsed : ALL_LEVELS;
  }

  private parseEntry(raw: string): LogEntry {
    let level: LogLevel = 'INFO';
    let timestamp = new Date();
    try {
      const parsed = JSON.parse(raw);
      if (ALL_LEVELS.includes(parsed.level)) level = parsed.level as LogLevel;
      // Python formatTime: "2024-01-15 10:30:45,123" — fix separators for Date()
      const tsStr = String(parsed.timestamp ?? '').replace(',', '.').replace(' ', 'T');
      const d = new Date(tsStr);
      if (!isNaN(d.getTime())) timestamp = d;
    } catch { /* non-JSON line; treat as INFO with current time */ }
    return { raw, level, timestamp };
  }

  private recomputeLogs(): void {
    this.logs = this.allLogs
      .filter(e => this.activeLevels.has(e.level))
      .map(e => e.raw)
      .join('\n\n');
    // onDidChangeModelContent handles scroll if following
  }

  public setMaxAge(hours: number): void {
    this.maxAgeHours = hours;
    setCookie('mmpm-log-max-age-h', String(hours));
    this.pruneOldLogs();
  }

  private pruneOldLogs(): void {
    const cutoff = Date.now() - this.maxAgeHours * 60 * 60 * 1000;
    const before = this.allLogs.length;
    this.allLogs = this.allLogs.filter(e => e.timestamp.getTime() >= cutoff);
    if (this.allLogs.length !== before) {
      this.zone.run(() => this.recomputeLogs());
    }
  }

  private loadMaxAgeCookie(): number {
    const raw = getCookie('mmpm-log-max-age-h', String(DEFAULT_MAX_AGE_H));
    const parsed = Number(raw);
    return (MAX_AGE_OPTIONS as readonly number[]).includes(parsed) ? parsed : DEFAULT_MAX_AGE_H;
  }
}
