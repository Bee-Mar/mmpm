
export interface MagicMirrorPackage {
  title: string;
  category: string;
  repository: string;
  author: string;
  description: string;
  directory: string;
}

export interface InstallationConflict {
  matchesInstalledTitles: Array<MagicMirrorPackage>;
  matchesSelectedTitles: Array<MagicMirrorPackage>;
}

export interface ActiveProcess {
  name: string;
  startTime: string;
}

