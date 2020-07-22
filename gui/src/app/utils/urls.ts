export const URLS = {
  GET: {
    PACKAGES: {
      _ROOT: "/packages",
      get MARKETPLACE() { return `${this._ROOT}/marketplace`; },
      get INSTALLED() { return `${this._ROOT}/installed`; },
      get EXTERNAL() { return `${this._ROOT}/external`; },
      get UPDATE() { return `${this._ROOT}/update`; },
      get UPGRADEABLE() { return `${this._ROOT}/upgradeable`; },
    },

    MAGICMIRROR: {
      _ROOT: "/magicmirror",
      get START() { return `${this._ROOT}/start`; },
      get STOP() { return `${this._ROOT}/stop`; },
      get RESTART() { return `${this._ROOT}/restart`; },
      get UPGRADE() { return `${this._ROOT}/upgrade`; },
      get CONFIG() { return `${this._ROOT}/config`; },
      get CUSTOM_CSS() { return `${this._ROOT}/custom-css`; },
    },

    MMPM: {
      _ROOT: "/mmpm",
      get DOWNLOAD_LOGS() { return `${this._ROOT}/download-logs`; },
      get ENVIRONMENT_VARS() { return `${this._ROOT}/environment-vars`},
      get ENVIRONMENT_VARS_FILE() { return `${this._ROOT}/environment-vars-file`}
    },

    RASPBERRYPI: {
      _ROOT: "/raspberrypi",
      get STOP() { return `${this._ROOT}/stop`; },
      get RESTART() { return `${this._ROOT}/restart`; },
    },
  },

  POST: {
    PACKAGES: {
      _ROOT: "/packages",
      get REMOVE() { return `${this._ROOT}/remove`; },
      get INSTALL() { return `${this._ROOT}/install`; },
      get UPGRADE() { return `${this._ROOT}/upgrade`; },
      get DETAILS() { return `${this._ROOT}/details`; },
    },

    EXTERNAL_PACKAGES: {
      _ROOT: "/external-packages",
      get ADD() { return `${this._ROOT}/add`; },
    },

    UPGRADE: {
      _ROOT: "/upgrade",
      get PACKAGES() { return `${this._ROOT}/packages`; },
      get EXTERNAL_PACKAGE() { return `${this._ROOT}/magicmirror`; },
    },

    MAGICMIRROR: {
      _ROOT: "/magicmirror",
      get CONFIG() { return `${this._ROOT}/config`; },
      get CUSTOM_CSS() { return `${this._ROOT}/custom-css`; },
      get INSTALL_MMPM_MODULE() { return `${this._ROOT}/install-mmpm-module`; }
    },

    RASPBERRYPI: {
      _ROOT: "/raspberrypi",
      get ROTATE_SCREEN() { return `${this._ROOT}/rotate-screen` },
    },

    MMPM: {
      _ROOT: "/mmpm",
      get ENVIRONMENT_VARS_FILE() { return `${this._ROOT}/environment-vars-file`; },
    },
  },

  DELETE: {
    EXTERNAL_PACKAGES: {
      _ROOT: "/external-packages",
      get REMOVE() { return `${this._ROOT}/remove`; },
    },
  }
};


