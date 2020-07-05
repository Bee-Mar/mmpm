export interface MagicMirrorPackage {
  title: string;
  repository: string;
  author: string;
  description: string;
  directory: string;
  category: string;
}

export interface InstallationConflict {
  matchesInstalledTitles: Array<MagicMirrorPackage>;
  matchesSelectedTitles: Array<MagicMirrorPackage>;
}

export interface ActiveProcess {
  name: string;
  startTime: string;
}
