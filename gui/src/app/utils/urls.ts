export const URLS = {
  GET: {
    PACKAGES: {
      ROOT: "/packages",
      get MARKETPLACE() { return `${this.ROOT}/marketplace`; },
      get INSTALLED() { return `${this.ROOT}/installed`; },
      get EXTERNAL() { return `${this.ROOT}/external`; },
      get UPDATE() { return `${this.ROOT}/update`; },
      get UPGRADEABLE() { return `${this.ROOT}/upgradeable`; },
    },

    DATABASE: {
      ROOT: "/database",
      get REFRESH() { return `${this.ROOT}/refresh`; },
    },

    MAGICMIRROR: {
      ROOT: "/magicmirror",
      get START() { return `${this.ROOT}/start`; },
      get STOP() { return `${this.ROOT}/stop`; },
      get RESTART() { return `${this.ROOT}/restart`; },
      get UPGRADE() { return `${this.ROOT}/upgrade`; },
      get CONFIG() { return `${this.ROOT}/config`; },
      get CUSTOM_CSS() { return `${this.ROOT}/custom-css`; },
      get ROOT_DIR() { return `${this.ROOT}/root-dir`; }
    },

    // EXTERNAL_PACKAGES: {
    // },

    RASPBERRYPI: {
      ROOT: "/rasperrypi",
      get STOP() { return `${this.ROOT}/stop`; },
      get RESTART() { return `${this.ROOT}/restart`; },
    },
  },

  POST: {
    PACKAGES: {
      ROOT: "/packages",
      get REMOVE() { return `${this.ROOT}/remove`; },
      get INSTALL() { return `${this.ROOT}/install`; },
      get UPGRADE() { return `${this.ROOT}/upgrade`; },
      get DETAILS() { return `${this.ROOT}/details`; },
    },

    EXTERNAL_PACKAGES: {
      ROOT: "/external-packages",
      get ADD() { return `${this.ROOT}/add`; },
    },

    UPGRADE: {
      ROOT: "/upgrade",
      get PACKAGES() { return `${this.ROOT}/packages`; },
      get EXTERNAL_PACKAGE() { return `${this.ROOT}/magicmirror`; },
    },

    MAGICMIRROR: {
      ROOT: "/magicmirror",
      get CONFIG() { return `${this.ROOT}/config`; },
      get CUSTOM_CSS() { return `${this.ROOT}/custom-css`; },
    },

    MMPM: {
      ROOT: "/mmpm",
      get LOGS() { return `${this.ROOT}/logs`; },
    }
  },

  DELETE: {
    EXTERNAL_PACKAGES: {
      ROOT: "/external-packages",
      get REMOVE() { return `${this.ROOT}/remove`; },
    },
  }
};


