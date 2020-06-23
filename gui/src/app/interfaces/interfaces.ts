
export interface MagicMirrorPackage {
  title: string;
  category: string;
  repository: string;
  author: string;
  description: string;
  directory: string;
}

export interface InstallationConflict {
  existingTitles: Array<MagicMirrorPackage>;
  duplicateTitles: Array<MagicMirrorPackage>;
}

export interface ActiveProcess {
  name: string;
  startTime: string;
}

