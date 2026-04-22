import { Component, OnInit, OnDestroy, ViewChild, inject } from '@angular/core';
import { MagicMirrorPackage } from '@/models/magicmirror-package';
import { SharedStoreService } from '@/services/shared-store.service';
import { ConfigFileAPI } from '@/services/api/config-file-api.service';
import { MessageService, MenuItem } from 'primeng/api';
import { ContextMenu } from 'primeng/contextmenu';
import { Subscription } from 'rxjs';
import { getModuleIcon, ModuleIcon } from '@/utils/module-icon';

interface Region {
  key: string;
  label: string;
  gridArea: string;
}

interface LibraryEntry {
  name: string;
  title: string;
}

type MirrorLayout = { [region: string]: string[] };  // values are module folder names

const REGIONS: Region[] = [
  { key: 'top_left',      label: 'TOP_LEFT',      gridArea: 'tl' },
  { key: 'top_bar',       label: 'TOP_BAR',        gridArea: 'tb' },
  { key: 'top_right',     label: 'TOP_RIGHT',      gridArea: 'tr' },
  { key: 'upper_third',   label: 'UPPER_THIRD',    gridArea: 'ml' },
  { key: 'middle_center', label: 'MIDDLE_CENTER',  gridArea: 'mc' },
  { key: 'lower_third',   label: 'LOWER_THIRD',    gridArea: 'mr' },
  { key: 'bottom_left',   label: 'BOTTOM_LEFT',    gridArea: 'bl' },
  { key: 'bottom_bar',    label: 'BOTTOM_BAR',     gridArea: 'bb' },
  { key: 'bottom_right',  label: 'BOTTOM_RIGHT',   gridArea: 'br' },
];

const STORAGE_KEY  = 'mmpm.mirror-layout-v2';
const DISABLED_KEY = 'mmpm.mirror-disabled';
const KNOWN_KEY    = 'mmpm.mirror-known';

function emptyLayout(): MirrorLayout {
  return Object.fromEntries(REGIONS.map(r => [r.key, []]));
}

@Component({
  selector: 'app-mirror-preview',
  templateUrl: './mirror-preview.component.html',
  styleUrls: ['./mirror-preview.component.scss'],
  providers: [MessageService],
  standalone: false,
})
export class MirrorPreviewComponent implements OnInit, OnDestroy {
  @ViewChild('contextMenu') contextMenu!: ContextMenu;

  private store = inject(SharedStoreService);
  private configApi = inject(ConfigFileAPI);
  private msg = inject(MessageService);
  private sub = new Subscription();

  public readonly regions = REGIONS;

  public packages: MagicMirrorPackage[] = [];
  public layout: MirrorLayout = emptyLayout();
  public disabledNames = new Set<string>();
  public contextMenuItems: MenuItem[] = [];
  public loading = true;
  public dragOverRegion: string | null = null;
  public draggingName: string | null = null;
  public libraryDragOver = false;
  public flashRegion: string | null = null;
  private flashTimer: ReturnType<typeof setTimeout> | null = null;

  // All module names ever seen in config.js (built-ins + MMPM packages)
  private knownModuleNames = new Set<string>();
  // module folder name → package for display title lookups
  private pkgByDir = new Map<string, MagicMirrorPackage>();

  // ── Initialisation ────────────────────────────────────────────────────────

  public ngOnInit(): void {
    this.sub = this.store.packages.subscribe(pkgs => {
      this.packages = pkgs;
      this.pkgByDir = new Map(pkgs.map(p => [p.directory?.toLowerCase(), p]));
    });

    const savedDisabled = localStorage.getItem(DISABLED_KEY);
    if (savedDisabled) {
      try { this.disabledNames = new Set(JSON.parse(savedDisabled)); } catch { /* ignore */ }
    }

    const savedKnown = localStorage.getItem(KNOWN_KEY);
    if (savedKnown) {
      try { this.knownModuleNames = new Set(JSON.parse(savedKnown)); } catch { /* ignore */ }
    }

    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        const hasModules = Object.values(parsed).some(
          (arr: unknown) => Array.isArray(arr) && arr.length > 0
        );
        if (hasModules) {
          this.layout = parsed;
          // Seed knownModuleNames from every module currently in the layout so
          // built-ins dragged to the library don't vanish on subsequent loads.
          for (const names of Object.values(this.layout)) {
            for (const name of names) {
              this.knownModuleNames.add(name);
            }
          }
          this.loading = false;
          return;
        }
      } catch { /* fall through to config.js parse */ }
    }

    this.configApi.getConfigFile('config.js').then(source => {
      this.layout = this.parseConfigJs(source);
      this.saveLayout();
    }).catch(() => {
      this.layout = emptyLayout();
    }).finally(() => {
      this.loading = false;
    });
  }

  public ngOnDestroy(): void {
    this.sub.unsubscribe();
    if (this.flashTimer) clearTimeout(this.flashTimer);
  }

  // ── Config.js parser ──────────────────────────────────────────────────────

  private parseConfigJs(source: string): MirrorLayout {
    const stripped = source
      .replace(/\/\*[\s\S]*?\*\//g, '')
      .replace(/\/\/.*/g, '');

    const layout = emptyLayout();
    const validRegions = new Set(REGIONS.map(r => r.key));
    const disabled = new Set<string>();

    for (const block of this.extractModuleBlocks(stripped)) {
      const modMatch = /module\s*:\s*["'`]([^"'`]+)["'`]/.exec(block);
      const posMatch = /position\s*:\s*["'`]([^"'`]+)["'`]/.exec(block);
      if (!modMatch) continue;

      const name = modMatch[1];
      const pos  = posMatch?.[1];

      this.knownModuleNames.add(name);

      if (pos && validRegions.has(pos)) {
        layout[pos].push(name);
      }

      if (/disabled\s*:\s*true/.test(block)) {
        disabled.add(name);
      }
    }

    this.disabledNames = disabled;
    this.saveDisabled();
    this.saveKnown();

    return layout;
  }

  /** Extracts balanced { } blocks that are direct children of the modules array. */
  private extractModuleBlocks(source: string): string[] {
    return this.extractModuleBlocksWithOffsets(source).map(b => b.block);
  }

  /** Same as extractModuleBlocks but returns start/end offsets in source. */
  private extractModuleBlocksWithOffsets(source: string): Array<{ block: string; start: number; end: number }> {
    const blocks: Array<{ block: string; start: number; end: number }> = [];
    const startIdx = source.search(/\bmodules\s*:/);
    if (startIdx === -1) return blocks;

    const arrOpen = source.indexOf('[', startIdx);
    if (arrOpen === -1) return blocks;

    let depth = 0;
    let blockStart = -1;

    for (let i = arrOpen + 1; i < source.length; i++) {
      const ch = source[i];
      if (ch === ']' && depth === 0) break;
      if (ch === '{') {
        if (depth === 0) blockStart = i;
        depth++;
      } else if (ch === '}') {
        depth--;
        if (depth === 0 && blockStart !== -1) {
          blocks.push({ block: source.slice(blockStart, i + 1), start: blockStart, end: i + 1 });
          blockStart = -1;
        }
      }
    }

    return blocks;
  }

  /** Returns a copy of source with each placed module's position and disabled state updated.
   *  Modules placed in the layout that have no existing config.js entry are appended. */
  private applyLayoutToConfigJs(source: string): string {
    const newPos = new Map<string, string>();
    for (const [region, names] of Object.entries(this.layout)) {
      for (const name of names) {
        newPos.set(name, region);
      }
    }

    const blocks = [...this.extractModuleBlocksWithOffsets(source)].reverse();
    let result = source;
    const existingNames = new Set<string>();

    for (const { block, start, end } of blocks) {
      const stripped = block
        .replace(/\/\*[\s\S]*?\*\//g, '')
        .replace(/\/\/.*/g, '');
      const modMatch = /module\s*:\s*["'`]([^"'`]+)["'`]/.exec(stripped);
      if (!modMatch) continue;

      const name = modMatch[1];
      existingNames.add(name);
      let newBlock = block;

      const desiredPos = newPos.get(name);
      if (desiredPos !== undefined) {
        const posRegex = /position\s*:\s*["'`][^"'`]*["'`]/;
        if (posRegex.test(newBlock)) {
          newBlock = newBlock.replace(posRegex, `position: "${desiredPos}"`);
        } else {
          newBlock = newBlock.replace(
            /(module\s*:\s*["'`][^"'`]*["'`])/,
            `$1,\n\t\t\tposition: "${desiredPos}"`
          );
        }
      }

      const isDisabled = this.disabledNames.has(name);
      const disabledRegex = /disabled\s*:\s*(true|false)/;
      if (disabledRegex.test(newBlock)) {
        if (isDisabled) {
          newBlock = newBlock.replace(disabledRegex, 'disabled: true');
        } else {
          newBlock = newBlock.replace(/,?\s*disabled\s*:\s*false\s*,?/, (m) =>
            m.startsWith(',') && m.endsWith(',') ? ',' : ''
          );
        }
      } else if (isDisabled) {
        newBlock = newBlock.replace(
          /(module\s*:\s*["'`][^"'`]*["'`])/,
          `$1,\n\t\t\tdisabled: true`
        );
      }

      result = result.slice(0, start) + newBlock + result.slice(end);
    }

    // Append entries for modules placed in the layout that aren't in config.js yet
    const newEntries: string[] = [];
    for (const [region, names] of Object.entries(this.layout)) {
      for (const name of names) {
        if (!existingNames.has(name)) {
          const disabledLine = this.disabledNames.has(name) ? ',\n\t\t\tdisabled: true' : '';
          newEntries.push(`\t\t{\n\t\t\tmodule: "${name}",\n\t\t\tposition: "${region}"${disabledLine}\n\t\t}`);
        }
      }
    }

    if (newEntries.length > 0) {
      const startIdx = result.search(/\bmodules\s*:/);
      if (startIdx !== -1) {
        const arrOpen = result.indexOf('[', startIdx);
        if (arrOpen !== -1) {
          let depth = 0;
          let arrClose = -1;
          for (let i = arrOpen; i < result.length; i++) {
            if (result[i] === '[') depth++;
            else if (result[i] === ']') { depth--; if (depth === 0) { arrClose = i; break; } }
          }
          if (arrClose !== -1) {
            result = result.slice(0, arrClose) + ',\n' + newEntries.join(',\n') + '\n\t' + result.slice(arrClose);
          }
        }
      }
    }

    return result;
  }

  // ── Derived state ─────────────────────────────────────────────────────────

  public get placedNames(): Set<string> {
    return new Set(Object.values(this.layout).flat());
  }

  public get placedCount(): number {
    return Object.values(this.layout).flat().length;
  }

  /**
   * Unplaced entries for the library panel.
   * Includes MMPM-installed packages and any built-in modules seen in config.js.
   */
  public get library(): LibraryEntry[] {
    const placed = this.placedNames;

    // All MMPM package directories (used to avoid duplicating them as builtins)
    const allPkgDirs = new Set(
      this.packages.map(p => p.directory?.toLowerCase()).filter((d): d is string => !!d)
    );

    // MMPM packages that are installed but not placed
    const pkgEntries: LibraryEntry[] = this.packages
      .filter(p => {
        if (!p.is_installed) return false;
        const dir = p.directory?.toLowerCase() ?? '';
        return dir && !placed.has(dir) && !placed.has(p.directory);
      })
      .map(p => ({ name: p.directory ?? p.title, title: p.title }));

    // Built-in / other module names known from config.js, not placed, not an MMPM package
    const builtinEntries: LibraryEntry[] = [...this.knownModuleNames]
      .filter(name => !placed.has(name) && !allPkgDirs.has(name.toLowerCase()))
      .map(name => ({ name, title: this.pkgByDir.get(name.toLowerCase())?.title ?? name }));

    return [...pkgEntries, ...builtinEntries];
  }

  public modulesInRegion(region: string): string[] {
    return this.layout[region] ?? [];
  }

  public displayTitle(name: string): string {
    return this.pkgByDir.get(name.toLowerCase())?.title ?? name;
  }

  public isDisabled(name: string): boolean {
    return this.disabledNames.has(name);
  }

  public getModuleIcon(entry: LibraryEntry): ModuleIcon {
    const pkg = this.pkgByDir.get(entry.name.toLowerCase());
    return getModuleIcon({ title: entry.title, directory: entry.name, category: pkg?.category });
  }

  public getModuleIconForName(name: string): ModuleIcon {
    const pkg = this.pkgByDir.get(name.toLowerCase());
    return getModuleIcon({ title: this.displayTitle(name), directory: name, category: pkg?.category });
  }

  // ── Context menu ──────────────────────────────────────────────────────────

  public onContextMenu(event: MouseEvent, name: string): void {
    event.preventDefault();
    const disabled = this.disabledNames.has(name);
    this.contextMenuItems = [
      {
        label: disabled ? 'Enable module' : 'Disable module',
        icon: disabled ? 'fa fa-eye' : 'fa fa-eye-slash',
        command: () => this.toggleDisabled(name),
      },
    ];
    this.contextMenu.show(event);
  }

  private toggleDisabled(name: string): void {
    if (this.disabledNames.has(name)) {
      this.disabledNames.delete(name);
    } else {
      this.disabledNames.add(name);
    }
    this.disabledNames = new Set(this.disabledNames);
    this.saveDisabled();
  }

  // ── Drag & Drop ───────────────────────────────────────────────────────────

  public onDragStartName(e: DragEvent, name: string): void {
    e.dataTransfer!.setData('text/plain', name);
    e.dataTransfer!.effectAllowed = 'move';
    this.draggingName = name;
  }

  public onDragStartEntry(e: DragEvent, entry: LibraryEntry): void {
    this.onDragStartName(e, entry.name);
  }

  public onDragEnd(): void {
    this.draggingName = null;
    this.dragOverRegion = null;
    this.libraryDragOver = false;
  }

  public onDragOver(e: DragEvent, region: string): void {
    e.preventDefault();
    e.dataTransfer!.dropEffect = 'move';
    this.dragOverRegion = region;
  }

  public onDragLeave(e: DragEvent): void {
    if (!(e.currentTarget as Element).contains(e.relatedTarget as Node)) {
      this.dragOverRegion = null;
    }
  }

  public onDrop(e: DragEvent, toRegion: string): void {
    e.preventDefault();
    const name = e.dataTransfer!.getData('text/plain');
    if (name) {
      this.moveToRegion(name, toRegion);
      this.triggerFlash(toRegion);
    }
    this.dragOverRegion = null;
    this.draggingName = null;
    this.saveLayout();
  }

  private triggerFlash(region: string): void {
    if (this.flashTimer) clearTimeout(this.flashTimer);
    this.flashRegion = region;
    this.flashTimer = setTimeout(() => { this.flashRegion = null; }, 480);
  }

  public onLibraryDragOver(e: DragEvent): void {
    e.preventDefault();
    this.libraryDragOver = true;
  }

  public onLibraryDragLeave(e: DragEvent): void {
    if (!(e.currentTarget as Element).contains(e.relatedTarget as Node)) {
      this.libraryDragOver = false;
    }
  }

  public onLibraryDrop(e: DragEvent): void {
    e.preventDefault();
    const name = e.dataTransfer!.getData('text/plain');
    if (name) this.removeFromLayout(name);
    this.libraryDragOver = false;
    this.draggingName = null;
    this.dragOverRegion = null;
    this.saveLayout();
  }

  private moveToRegion(name: string, toRegion: string): void {
    const next = emptyLayout();
    for (const [k, arr] of Object.entries(this.layout)) {
      next[k] = arr.filter(n => n !== name);
    }
    next[toRegion] = [...(next[toRegion] ?? []), name];
    this.layout = next;
  }

  private removeFromLayout(name: string): void {
    const next: MirrorLayout = {};
    for (const [k, arr] of Object.entries(this.layout)) {
      next[k] = arr.filter(n => n !== name);
    }
    this.layout = next;
  }

  // ── Persistence ───────────────────────────────────────────────────────────

  private saveLayout(): void {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(this.layout));
  }

  private saveDisabled(): void {
    localStorage.setItem(DISABLED_KEY, JSON.stringify([...this.disabledNames]));
  }

  private saveKnown(): void {
    localStorage.setItem(KNOWN_KEY, JSON.stringify([...this.knownModuleNames]));
  }

  public resetLayout(): void {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(DISABLED_KEY);
    localStorage.removeItem(KNOWN_KEY);
    this.knownModuleNames.clear();
    this.loading = true;
    this.configApi.getConfigFile('config.js').then(source => {
      this.layout = this.parseConfigJs(source);
      this.saveLayout();
    }).catch(() => {
      this.layout = emptyLayout();
    }).finally(() => {
      this.loading = false;
    });
    this.msg.add({ severity: 'info', summary: 'Mirror Preview', detail: 'Layout reset from config.js' });
  }

  public saveToConfig(): void {
    this.saveLayout();
    this.saveDisabled();
    this.configApi.getConfigFile('config.js')
      .then(source => this.configApi.postConfigFile('config.js', this.applyLayoutToConfigJs(source)))
      .then(() => {
        this.msg.add({ severity: 'success', summary: 'Mirror Preview', detail: 'Layout saved to config.js' });
      })
      .catch(() => {
        this.msg.add({ severity: 'error', summary: 'Mirror Preview', detail: 'Failed to write config.js' });
      });
  }
}
