import { MagicMirrorPackage } from "./magicmirror-package";

export interface UpgradableDetails {
  mmpm: boolean;
  MagicMirror: boolean;
  packages: Array<MagicMirrorPackage>;
}
