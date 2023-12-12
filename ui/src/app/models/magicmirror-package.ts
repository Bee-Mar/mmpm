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
}

export interface RemotePackageDetails {
  stars: number;
  issues: number;
  created: string;
  last_updated: string;
  forks: number;
}
