export interface MagicMirrorPackage {
  title: string;
  author: string;
  repository: string;
  description: string;
  directory: string;
  category: string;
  is_installed: boolean;
  is_upgradable: boolean;
  remote_details: RemotePackageDetails;
  stars: number;
  last_updated: string;
  license?: string;
}

export interface RemotePackageDetails {
  issues: number;
  created: string;
  forks: number;
}
