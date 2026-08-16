import {
  Component,
  HostListener,
  OnDestroy,
  OnInit,
  ViewChild,
  inject,
} from '@angular/core';
import { EditorComponent } from 'ngx-monaco-editor-v2';
import { Subscription } from 'rxjs';
import { getCookie, setCookie } from '@/utils/utils';
import { ConfigFileAPI } from '@/services/api/config-file-api.service';
import { EnvApiService, EnvVarInfo } from '@/services/api/env-api.service';
import { MessageService } from 'primeng/api';
import { APIResponse } from '@/services/api/base-api';
import { SharedStoreService } from '@/services/shared-store.service';
import { MagicMirrorPackage } from '@/models/magicmirror-package';

interface FileContentsState {
  current: string;
  saved: string;
  language: string;
}

@Component({
  selector: 'app-config-editor',
  templateUrl: './config-editor.component.html',
  styleUrls: ['./config-editor.component.scss'],
  providers: [MessageService],
  standalone: false,
})
export class ConfigEditorComponent implements OnInit, OnDestroy {
  private configFileApi = inject(ConfigFileAPI);
  private envApi = inject(EnvApiService);
  private store = inject(SharedStoreService);
  private msg = inject(MessageService);

  public showEnvInfo = false;
  public envDescriptions: EnvVarInfo[] = [];
  public uninstalledModules: string[] = [];

  private packages: MagicMirrorPackage[] = [];
  private pkgSub = new Subscription();

  @ViewChild(EditorComponent, { static: false })
  public editor: EditorComponent;

  public file = getCookie('mmpm-config-editor-selected-file', 'config.js');
  public fontSize = Number(getCookie('mmpm-config-editor-font-size', '12'));

  public state: { [key: string]: FileContentsState } = {
    'config.js': {
      current: '',
      saved: '',
      language: 'javascript',
    },
    'mmpm-env.json': {
      current: '',
      saved: '',
      language: 'json',
    },
    'custom.css': {
      current: '',
      saved: '',
      language: 'css',
    },
  };

  public get fileNames(): string[] {
    return Object.keys(this.state);
  }

  public fileOptions = [
    {
      label: 'config.js',
      icon: 'fa-solid fa-code',
      command: () => {
        this.onSelectFile('config.js');
      },
    },
    {
      label: 'mmpm-env.json',
      icon: 'fa-solid fa-code',
      command: () => {
        this.onSelectFile('mmpm-env.json');
      },
    },
    {
      label: 'custom.css',
      icon: 'fa-solid fa-code',
      command: () => {
        this.onSelectFile('custom.css');
      },
    },
  ];

  public options = {
    language: 'javascript',
    theme: 'vs-dark',
    scrollBeyondLastLine: false,
    fontSize: this.fontSize,
    minimap: {
      enabled: false,
    },
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

  @HostListener('window:beforeunload', ['$event'])
  public beforeUnload($event: BeforeUnloadEvent) {
    if (this.state[this.file].current !== this.state[this.file].saved) {
      $event.returnValue = `You have unsaved changes made to ${this.file}. Are you sure you want to exit?`;
    }
  }

  public handleKeyDown(event: KeyboardEvent): void {
    if (event.ctrlKey && event.key === 's') {
      event.preventDefault();

      if (this.state[this.file].current !== this.state[this.file].saved) {
        this.onSaveFile();
      }
    }
  }

  public ngOnInit(): void {
    this.pkgSub = this.store.packages.subscribe(pkgs => {
      this.packages = pkgs;
      if (this.file === 'config.js' && this.state['config.js'].current) {
        this.checkUninstalledModules();
      }
    });
    this.onSelectFile(this.file);
  }

  public ngOnDestroy(): void {
    this.pkgSub.unsubscribe();
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  public onEditorInit(editor: any): void {
    this.editor = editor;
  }

  public onSelectFile(file: string): void {
    this.file = file;

    setCookie('mmpm-config-editor-selected-file', this.file);

    if (!this.state[file].current) {
      this.configFileApi.getConfigFile(this.file).then((contents: string) => {
        this.state[file].current = this.state[file].saved = contents;
        this.setLanguage();
        if (file === 'config.js') this.checkUninstalledModules();
      });
    } else {
      this.setLanguage();
      if (file === 'config.js') this.checkUninstalledModules();
    }
  }

  private setLanguage() {
    this.options = Object.assign({}, this.options, {
      language: this.state[this.file].language,
    });
  }

  public onSaveFile(): void {
    this.configFileApi
      .postConfigFile(this.file, this.state[this.file].current)
      .then((response: APIResponse) => {
        if (response.code === 200) {
          this.state[this.file].saved = this.state[this.file].current;
          this.store.load();
          if (this.file === 'config.js') {
            this.store.notifyConfigJsSaved();
            this.checkUninstalledModules();
          }
          this.msg.add({
            severity: 'success',
            summary: 'Save File',
            detail: `Saved ${this.file}`,
          });
        } else {
          console.log(response.message);
          this.msg.add({
            severity: 'error',
            summary: 'Save File',
            detail: response.message,
          });
        }
      });
  }

  private checkUninstalledModules(): void {
    const source = this.state['config.js'].current
      .replace(/\/\*[\s\S]*?\*\//g, '')
      .replace(/\/\/.*/g, '');
    const pkgByDir = new Map(this.packages.map(p => [p.directory?.toLowerCase(), p]));
    const uninstalled = new Set<string>();
    const re = /module\s*:\s*["'`]([^"'`]+)["'`]/g;
    let match: RegExpExecArray | null;
    while ((match = re.exec(source)) !== null) {
      const pkg = pkgByDir.get(match[1].toLowerCase());
      if (pkg && !pkg.is_installed) uninstalled.add(match[1]);
    }
    this.uninstalledModules = [...uninstalled];
  }

  public onFontSizeChange(): void {
    setCookie('mmpm-config-editor-font-size', String(this.fontSize));
    this.options = Object.assign({}, this.options, { fontSize: this.fontSize });
  }

  public openEnvInfo(): void {
    if (this.envDescriptions.length === 0) {
      this.envApi.getDescriptions().then((items) => {
        this.envDescriptions = items;
        this.showEnvInfo = true;
      });
    } else {
      this.showEnvInfo = true;
    }
  }
}
